"""
Liquidity Regime Discord Bot
Slash commands + automatic alerts for regime changes
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import tasks

# Add parent dir for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.fetchers import fetch_all_data
from data.transforms import calculate_metrics
from scoring.engine import calculate_scores
from scoring.regime import determine_regime

intents = discord.Intents.default()
intents.message_content = True


class LiquidityBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.subscribed_channels = set()
        self.last_regime = None
        self.data_cache = {}
        self.cache_time = None
        self.subs_file = Path(__file__).parent / "subscribed_channels.json"
        self.load_subscriptions()

    def load_subscriptions(self):
        if self.subs_file.exists():
            try:
                with open(self.subs_file) as f:
                    self.subscribed_channels = set(json.load(f))
            except:
                pass

    def save_subscriptions(self):
        with open(self.subs_file, "w") as f:
            json.dump(list(self.subscribed_channels), f)

    async def setup_hook(self):
        await self.tree.sync()
        print("Synced slash commands")

    def get_data(self, force_refresh=False):
        now = datetime.now()
        if not force_refresh and self.cache_time and (now - self.cache_time).seconds < 1800:
            return self.data_cache

        print("Fetching fresh data...")
        data = fetch_all_data()
        metrics = calculate_metrics(data)
        scores = calculate_scores(metrics)
        state_file = Path(__file__).parent.parent / "regime_state.json"
        regime, state, regime_info = determine_regime(scores, state_file=state_file)

        self.data_cache = {
            "metrics": metrics,
            "scores": scores,
            "regime": regime,
        }
        self.cache_time = now
        return self.data_cache


bot = LiquidityBot()

REGIME_COLORS = {
    "aggressive": discord.Color.green(),
    "balanced": discord.Color.gold(),
    "defensive": discord.Color.red(),
}

REGIME_DESCRIPTIONS = {
    "aggressive": "Liquidity conditions look favorable. Macro tailwinds support risk-on positioning.",
    "balanced": "Mixed signals across indicators. Stay selective and avoid overexposure.",
    "defensive": "Liquidity headwinds present. Consider reducing risk and preserving capital.",
}

METRIC_NAMES = {
    "walcl": "Fed Balance Sheet",
    "rrp": "Reverse Repo",
    "hy_spread": "Credit Spreads",
    "dxy": "Dollar Strength",
    "stablecoin": "Stablecoin Flows",
}


def create_regime_embed(cache_data, include_signals=True):
    regime = cache_data["regime"]
    scores = cache_data["scores"]
    metrics = cache_data["metrics"]

    total_score = scores.get("total", 0)
    btc_data = metrics.get("btc", {})
    btc_price = btc_data.get("current_price")
    btc_200dma = btc_data.get("ma_200")
    btc_above = scores.get("btc_above_200dma", False)

    color = REGIME_COLORS.get(regime, discord.Color.blurple())
    description = REGIME_DESCRIPTIONS.get(regime, "")

    embed = discord.Embed(
        title=f"{regime.upper()} - Score: {total_score:+.1f}",
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )

    btc_str = f"${btc_price:,.0f}" if btc_price else "N/A"
    btc_ma_str = f"${btc_200dma:,.0f}" if btc_200dma else "N/A"
    btc_vs = "above" if btc_above else "below"
    embed.add_field(name="BTC", value=f"**{btc_str}** ({btc_vs} {btc_ma_str} MA)", inline=True)

    dashboard_url = os.environ.get("DASHBOARD_URL", "https://liquidity-dashboard.streamlit.app")
    embed.add_field(name="Learn More", value=f"[Dashboard]({dashboard_url})", inline=True)

    if include_signals:
        lines = []
        for name, data in scores.get("individual", {}).items():
            sig = data.get("score", 0)
            icon = "+" if sig > 0 else "-" if sig < 0 else "o"
            lines.append(f"[{icon}] {METRIC_NAMES.get(name, name)}")
        embed.add_field(name="Signals", value="\n".join(lines) or "No data", inline=False)

    embed.set_footer(text="Liquidity Regime Bot")
    return embed


@bot.tree.command(name="regime", description="Get the current liquidity regime and score")
async def regime_command(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        cache_data = bot.get_data()
        embed = create_regime_embed(cache_data)
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"Error fetching data: {str(e)}", ephemeral=True)


@bot.tree.command(name="btc", description="Get Bitcoin price vs 200-day moving average")
async def btc_command(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        cache_data = bot.get_data()
        metrics = cache_data["metrics"]
        scores = cache_data["scores"]

        btc_data = metrics.get("btc", {})
        btc_price = btc_data.get("current_price")
        btc_200dma = btc_data.get("ma_200")
        btc_above = scores.get("btc_above_200dma", False)
        distance = btc_data.get("distance_from_200dma", 0)

        color = discord.Color.green() if btc_above else discord.Color.red()
        status = "above" if btc_above else "below"

        embed = discord.Embed(
            title=f"BTC: ${btc_price:,.0f}" if btc_price else "Bitcoin",
            description=f"Currently **{status}** the 200-day moving average",
            color=color,
            timestamp=datetime.utcnow()
        )

        if btc_200dma:
            embed.add_field(name="200 DMA", value=f"${btc_200dma:,.0f}", inline=True)
        if distance:
            embed.add_field(name="Distance", value=f"{distance * 100:+.1f}%", inline=True)

        embed.add_field(
            name="Why it matters",
            value="BTC must be above its 200 DMA for an Aggressive regime signal.",
            inline=False
        )
        embed.set_footer(text="Liquidity Regime Bot")
        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)}", ephemeral=True)


@bot.tree.command(name="subscribe", description="Subscribe this channel to regime change alerts")
@app_commands.checks.has_permissions(manage_channels=True)
async def subscribe_command(interaction: discord.Interaction):
    channel_id = interaction.channel_id

    if channel_id in bot.subscribed_channels:
        await interaction.response.send_message("This channel is already subscribed!", ephemeral=True)
        return

    bot.subscribed_channels.add(channel_id)
    bot.save_subscriptions()

    embed = discord.Embed(
        title="Subscribed!",
        description="This channel will receive alerts when the liquidity regime changes.",
        color=discord.Color.green()
    )
    embed.set_footer(text="Use /unsubscribe to stop alerts")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="unsubscribe", description="Unsubscribe from regime alerts")
@app_commands.checks.has_permissions(manage_channels=True)
async def unsubscribe_command(interaction: discord.Interaction):
    channel_id = interaction.channel_id

    if channel_id not in bot.subscribed_channels:
        await interaction.response.send_message("This channel isn't subscribed.", ephemeral=True)
        return

    bot.subscribed_channels.discard(channel_id)
    bot.save_subscriptions()
    await interaction.response.send_message("Unsubscribed from alerts.", ephemeral=True)


@bot.tree.command(name="explain", description="Learn what this bot tracks and why it matters")
async def explain_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="What is Liquidity Regime?",
        description="Crypto moves with liquidity. This bot tracks the macro signals that matter.",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="What we track",
        value="Fed Balance Sheet, Reverse Repo, Credit Spreads, Dollar Strength, Stablecoin Flows",
        inline=False
    )

    embed.add_field(
        name="The Regimes",
        value="**Aggressive** - Risk on\n**Balanced** - Be selective\n**Defensive** - Reduce risk",
        inline=False
    )

    embed.add_field(
        name="Commands",
        value="`/regime` - Current regime\n`/btc` - BTC vs 200 DMA\n`/subscribe` - Get alerts\n`/explain` - This message",
        inline=False
    )

    dashboard_url = os.environ.get("DASHBOARD_URL", "https://liquidity-dashboard.streamlit.app")
    embed.add_field(name="Full Dashboard", value=f"[Open]({dashboard_url})", inline=False)
    embed.set_footer(text="Not financial advice")

    await interaction.response.send_message(embed=embed)


@tasks.loop(hours=4)
async def check_regime_changes():
    """Check for regime changes and alert subscribed channels."""
    if not bot.subscribed_channels:
        return

    try:
        cache_data = bot.get_data(force_refresh=True)
        current_regime = cache_data["regime"]

        if bot.last_regime is None:
            bot.last_regime = current_regime
            return

        if current_regime != bot.last_regime:
            print(f"Regime changed: {bot.last_regime} -> {current_regime}")

            regime_order = {"defensive": 0, "balanced": 1, "aggressive": 2}
            old_rank = regime_order.get(bot.last_regime, 1)
            new_rank = regime_order.get(current_regime, 1)
            direction = "Conditions improving" if new_rank > old_rank else "Conditions deteriorating"

            scores = cache_data["scores"]
            metrics = cache_data["metrics"]
            btc_price = metrics.get("btc", {}).get("current_price")
            btc_str = f"${btc_price:,.0f}" if btc_price else "N/A"

            embed = discord.Embed(
                title=f"Regime Change: {bot.last_regime.title()} -> {current_regime.title()}",
                description=f"**{direction}**\n\n{REGIME_DESCRIPTIONS.get(current_regime, '')}\n\nBTC: **{btc_str}** | Score: **{scores.get('total', 0):+.1f}**",
                color=REGIME_COLORS.get(current_regime, discord.Color.blurple()),
                timestamp=datetime.utcnow()
            )

            dashboard_url = os.environ.get("DASHBOARD_URL", "https://liquidity-dashboard.streamlit.app")
            embed.add_field(name="Learn More", value=f"[Open Dashboard]({dashboard_url})", inline=False)
            embed.set_footer(text="Liquidity Regime Alert")

            for channel_id in bot.subscribed_channels.copy():
                try:
                    channel = bot.get_channel(channel_id)
                    if channel:
                        await channel.send("Heads up - liquidity regime just changed:", embed=embed)
                except Exception as e:
                    print(f"Failed to send to channel {channel_id}: {e}")
                    bot.subscribed_channels.discard(channel_id)
                    bot.save_subscriptions()

            bot.last_regime = current_regime

    except Exception as e:
        print(f"Error checking regime: {e}")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"Subscribed channels: {len(bot.subscribed_channels)}")

    try:
        cache_data = bot.get_data()
        bot.last_regime = cache_data["regime"]
        print(f"Current regime: {bot.last_regime}")
    except Exception as e:
        print(f"Error getting initial regime: {e}")

    if not check_regime_changes.is_running():
        check_regime_changes.start()

    print("Bot is ready!")


if __name__ == "__main__":
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        print("ERROR: DISCORD_BOT_TOKEN not set")
        sys.exit(1)

    bot.run(token)
