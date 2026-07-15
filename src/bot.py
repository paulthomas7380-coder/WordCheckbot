async def process_check(update: Update, text: str, header: str, only_spelling: bool = False, only_grammar: bool = False):
    """Process the text check and send results."""
    try:
        # Truncate text if too long
        if len(text) > MAX_TEXT_LENGTH:
            text = text[:MAX_TEXT_LENGTH]
            await update.message.reply_text("⚠️ Text truncated to maximum length.")
        
        # Perform the check
        results = checker.full_check(text)
        
        # Update stats - FIXED: Use correct context
        stats = update.effective_user.bot_data.get('stats', {'total_checks': 0, 'total_errors': 0})
        stats['total_checks'] = stats.get('total_checks', 0) + 1
        stats['total_errors'] = stats.get('total_errors', 0) + results['total_issues']
        update.effective_user.bot_data['stats'] = stats
        
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
