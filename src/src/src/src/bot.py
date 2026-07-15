import logging
import html
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from src.config import TELEGRAM_TOKEN, MAX_TEXT_LENGTH, SUPPORTED_LANGUAGES
from src.checker import checker

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Keyboard layouts
def get_main_keyboard():
    """Create the main menu keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("📝 Check Spelling", callback_data="check_spelling"),
            InlineKeyboardButton("📖 Check Grammar", callback_data="check_grammar")
        ],
        [
            InlineKeyboardButton("🌐 Change Language", callback_data="change_language"),
            InlineKeyboardButton("ℹ️ Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("📊 Stats", callback_data="stats")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_language_keyboard():
    """Create language selection keyboard."""
    keyboard = []
    row = []
    for i, (code, name) in enumerate(SUPPORTED_LANGUAGES.items()):
        row.append(InlineKeyboardButton(name, callback_data=f"lang_{code}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    welcome_message = (
        f"👋 Hello {html.escape(user.first_name)}!\n\n"
        "🔍 *WordCheck Bot* is here to help you with:\n"
        "• ✏️ Spelling corrections\n"
        "• 📖 Grammar suggestions\n"
        "• 🌐 Multiple language support\n\n"
        "Send me any text, and I'll check it for errors!\n"
        "Or use the buttons below to get started."
    )
    await update.message.reply_text(
        welcome_message,
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message when /help is issued."""
    help_text = (
        "📚 *How to use WordCheck Bot*\n\n"
        "1️⃣ Send any text message\n"
        "2️⃣ Bot will automatically check spelling & grammar\n"
        "3️⃣ Get instant feedback with corrections\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/check - Check last sent text\n"
        "/stats - Show statistics\n"
        "/language - Change language\n"
        "/about - About this bot\n\n"
        "*Features:*\n"
        "✅ Spell checking in 12+ languages\n"
        "✅ Grammar suggestions\n"
        "✅ Auto-detection of language\n"
        "✅ Correction suggestions\n"
        "✅ Clean and easy-to-read results"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check the last text when /check is issued."""
    if not context.user_data.get('last_text'):
        await update.message.reply_text(
            "⚠️ No text found to check. Please send me some text first!"
        )
        return
    
    text = context.user_data['last_text']
    await process_check(update, text, "📝 *Results for your text:*\n\n")

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show language selection menu."""
    await update.message.reply_text(
        "🌐 *Select your preferred language:*",
        parse_mode="Markdown",
        reply_markup=get_language_keyboard()
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics."""
    stats = context.bot_data.get('stats', {})
    total_checks = stats.get('total_checks', 0)
    total_errors = stats.get('total_errors', 0)
    
    stats_text = (
        "📊 *Statistics*\n\n"
        f"Total texts checked: {total_checks}\n"
        f"Total errors found: {total_errors}\n"
        f"Current language: {SUPPORTED_LANGUAGES.get(checker.language, 'English')}\n\n"
        "Keep using the bot to improve your writing! 🚀"
    )
    await update.message.reply_text(stats_text, parse_mode="Markdown")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show about information."""
    about_text = (
        "🤖 *WordCheck Bot v1.0*\n\n"
        "Built with ❤️ using:\n"
        "• python-telegram-bot\n"
        "• pyspellchecker\n"
        "• language-tool-python\n\n"
        "📝 Check your text for spelling and grammar errors instantly!\n"
        "🌐 Supports multiple languages\n"
        "🔓 Open source on GitHub\n\n"
        "Made for writers, students, and professionals!"
    )
    await update.message.reply_text(about_text, parse_mode="Markdown")

# Callback Query Handlers
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_data = context.user_data
    
    if data == "check_spelling":
        if user_data.get('last_text'):
            await process_check(update, user_data['last_text'], "✏️ *Spelling Check Results:*\n\n", only_spelling=True)
        else:
            await query.edit_message_text("⚠️ No text found to check. Please send me some text first!")
            
    elif data == "check_grammar":
        if user_data.get('last_text'):
            await process_check(update, user_data['last_text'], "📖 *Grammar Check Results:*\n\n", only_grammar=True)
        else:
            await query.edit_message_text("⚠️ No text found to check. Please send me some text first!")
            
    elif data == "change_language":
        await query.edit_message_text(
            "🌐 *Select your preferred language:*",
            parse_mode="Markdown",
            reply_markup=get_language_keyboard()
        )
        
    elif data == "help":
        await query.edit_message_text(
            "📚 *How to use WordCheck Bot*\n\n"
            "Send any text and I'll check it for errors!\n"
            "Use the buttons below for specific checks.",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        
    elif data == "stats":
        await stats_command(update, context)
        
    elif data == "back":
        await query.edit_message_text(
            "🔍 *WordCheck Bot*\n\n"
            "What would you like to do?",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        
    elif data.startswith("lang_"):
        lang_code = data.split("_")[1]
        if checker.change_language(lang_code):
            lang_name = SUPPORTED_LANGUAGES.get(lang_code, lang_code)
            await query.edit_message_text(
                f"✅ Language changed to *{lang_name}*!\n\n"
                "Send me some text to check in the new language.",
                parse_mode="Markdown",
                reply_markup=get_main_keyboard()
            )
        else:
            await query.edit_message_text(
                "❌ Failed to change language. Please try again.",
                reply_markup=get_main_keyboard()
            )

# Message Handler
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages."""
    text = update.message.text
    
    # Skip commands
    if text.startswith('/'):
        return
    
    # Store the text for later use
    context.user_data['last_text'] = text
    
    # Update statistics
    stats = context.bot_data.get('stats', {'total_checks': 0, 'total_errors': 0})
    stats['total_checks'] = stats.get('total_checks', 0) + 1
    context.bot_data['stats'] = stats
    
    # Check the text
    await process_check(update, text, "🔍 *Checking your text...*\n\nHere are the results:\n\n")

async def process_check(update: Update, text: str, header: str, only_spelling: bool = False, only_grammar: bool = False):
    """Process the text check and send results."""
    try:
        # Truncate text if too long
        if len(text) > MAX_TEXT_LENGTH:
            text = text[:MAX_TEXT_LENGTH]
            await update.message.reply_text("⚠️ Text truncated to maximum length.")
        
        # Perform the check
        results = checker.full_check(text)
        
        # Update stats
        stats = context.bot_data.get('stats', {})
        stats['total_errors'] = stats.get('total_errors', 0) + results['total_issues']
        context.bot_data['stats'] = stats
        
        # Format response
        response = header
        
        # Spelling results
        if not only_grammar:
            spelling = results['spelling']
            if spelling['misspelled_count'] > 0:
                response += "✏️ *Spelling Errors:*\n"
                for word, correction in spelling['corrections'].items():
                    response += f"• ❌ *{word}* → ✅ {correction}\n"
                    if word in spelling['suggestions'] and spelling['suggestions'][word]:
                        suggestions = ', '.join(list(spelling['suggestions'][word])[:3])
                        response += f"  💡 Also try: {suggestions}\n"
                response += "\n"
            else:
                response += "✅ *No spelling errors found!* ✨\n\n"
        
        # Grammar results
        if not only_spelling:
            grammar = results['grammar']
            if grammar:
                response += "📖 *Grammar Suggestions:*\n"
                for issue in grammar[:5]:  # Limit to 5 issues
                    response += f"• ⚠️ {issue['message']}\n"
                    if issue['replacements']:
                        replacements = ', '.join(issue['replacements'][:3])
                        response += f"  💡 Try: {replacements}\n"
                if len(grammar) > 5:
                    response += f"\n*... and {len(grammar) - 5} more issues.*"
                response += "\n"
            else:
                response += "✅ *No grammar issues found!* ✨\n\n"
        
        # Summary
        if results['total_issues'] > 0:
            response += f"\n📊 *Summary:* {results['summary']}"
        else:
            response += "🎉 Your text looks great! No errors found."
        
        # Send the response
        await update.message.reply_text(
            response,
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in process_check: {e}")
        await update.message.reply_text(
            "❌ Sorry, an error occurred while checking your text. Please try again.",
            reply_markup=get_main_keyboard()
        )

# Error Handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors and notify user."""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ An unexpected error occurred. Please try again later."
        )

def main():
    """Start the bot."""
    # Create the Application
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Store statistics in bot_data
    app.bot_data['stats'] = {'total_checks': 0, 'total_errors': 0}
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("check", check_command))
    app.add_handler(CommandHandler("language", language_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("about", about_command))
    
    # Add callback query handler for buttons
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Add message handler for text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Add error handler
    app.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("🤖 WordCheck Bot is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
