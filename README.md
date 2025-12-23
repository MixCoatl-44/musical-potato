# BTC/ETH Pattern Scanner

Scans BTCUSDT and ETHUSDT on Binance for two custom setups:

- **Setup 1**: base → impulse → single wick retest into base → continuation breaking the swing high/low.  
  Timeframes: `1m`, `3m`, `1d`, `1w`.

- **Setup 2**: clean 0‑1‑2‑3 swing structure (two highs, two lows) with a one‑candle liquidity sweep and then
  a close beyond the starting point.  
  Timeframes: `15m`, `1h`, `4h`.

Alerts are sent via Telegram.

## Configuration

1. Create a Telegram bot via [@BotFather](https://t.me/BotFather) and note the bot token.
2. Start a chat with your bot, send any message, then visit:
   `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`  
   to find your `chat.id`.
3. In your GitHub repo, go to **Settings → Secrets and variables → Actions → New repository secret**:
   - `TELEGRAM_BOT_TOKEN` = your bot token
   - `TELEGRAM_CHAT_ID`   = your chat id

## How it runs

- GitHub Actions workflow `.github/workflows/run-bot.yml` runs `python main.py` every hour.
- `main.py` pulls recent candles from Binance, detects patterns, and sends Telegram alerts.

> Note: because the workflow is stateless and runs hourly, you might occasionally see duplicate alerts for
> the same pattern on higher timeframes (4h, 1d, 1w). For strict de‑duplication you’d need some persistent
> storage (database/file) to remember already‑alerted candles.
