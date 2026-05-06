import datetime

def get_quiz_report_html(student_name, score, total, percentage):
    """Generates a high-fidelity HTML email report for quiz results."""
    date_str = datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    # Determine color based on performance
    perf_color = "#48bb78" if percentage >= 70 else "#ed8936" if percentage >= 40 else "#f56565"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #2d3748; margin: 0; padding: 0; background-color: #f7fafc; }}
            .wrapper {{ padding: 20px; background-color: #f7fafc; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; }}
            .header h1 {{ margin: 0; font-size: 36px; font-weight: 800; }}
            .header p {{ margin: 10px 0 0 0; font-size: 16px; opacity: 0.9; }}
            .content {{ padding: 30px; }}
            .stat-card {{ background: #ffffff; border: 1px solid #edf2f7; padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); border-left: 4px solid {perf_color}; }}
            .stat-label {{ font-size: 13px; color: {perf_color}; font-weight: 700; margin-bottom: 8px; }}
            .stat-value {{ font-size: 32px; font-weight: 800; color: #1a202c; }}
            .footer {{ background: #2d3748; color: #ffffff; padding: 30px; text-align: center; }}
            .footer p {{ margin: 10px 0; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            <div class="container">
                <div class="header">
                    <h1>📝 Interactive Quiz Results</h1>
                    <p>Student: <b>{student_name}</b></p>
                    <p>Date: {date_str}</p>
                </div>
                
                <div class="content">
                    <div class="stat-card">
                        <div class="stat-label">🎯 Final Score</div>
                        <div class="stat-value">{score} / {total}</div>
                    </div>

                    <div class="stat-card">
                        <div class="stat-label">📈 Percentage</div>
                        <div class="stat-value">{percentage:.1f}%</div>
                    </div>

                    <h2 style="color: #667eea; margin-top: 30px;">{"Excellent Work! 🌟" if percentage >= 80 else "Good Job! 👍" if percentage >= 50 else "Keep Practicing! 💪"}</h2>
                    <p style="color: #718096;">You have successfully completed your interactive language quiz. Review your performance and continue your learning journey.</p>
                </div>

                <div class="footer">
                    <p><b>See you in the next session! 📚</b></p>
                    <p style="opacity: 0.7;">Powered by English Learning AI Agent</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def get_premium_report_html(student_name, duration, total_queries, avg_confidence, tool_counts):
    """Generates a high-fidelity HTML email report matching the professional design precisely."""
    
    # Generate tool list HTML with background bars
    tool_rows = ""
    for tool, count in tool_counts.items():
        tool_rows += f"""
        <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #667eea; display: flex; justify-content: space-between;">
            <span style="font-weight: bold; color: #333;">{tool}</span> 
            <span style="color: #666;">{count} times</span>
        </div>
        """

    date_str = datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p")

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #2d3748; margin: 0; padding: 0; background-color: #f7fafc; }}
            .wrapper {{ padding: 20px; background-color: #f7fafc; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; }}
            .header h1 {{ margin: 0; font-size: 36px; font-weight: 800; }}
            .header p {{ margin: 10px 0 0 0; font-size: 16px; opacity: 0.9; }}
            .content {{ padding: 30px; }}
            .stat-card {{ background: #ffffff; border: 1px solid #edf2f7; padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); border-left: 4px solid #667eea; }}
            .stat-label {{ font-size: 13px; color: #667eea; font-weight: 700; margin-bottom: 8px; }}
            .stat-value {{ font-size: 32px; font-weight: 800; color: #1a202c; }}
            .tool-section {{ background: #ffffff; border: 1px solid #edf2f7; padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #48bb78; }}
            .tool-label {{ font-size: 13px; color: #48bb78; font-weight: 700; margin-bottom: 15px; }}
            .footer {{ background: #2d3748; color: #ffffff; padding: 30px; text-align: center; }}
            .footer p {{ margin: 10px 0; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            <div class="container">
                <div class="header">
                    <h1>📊 Learning Session Summary</h1>
                    <p>Student: <b>{student_name}</b></p>
                    <p>Date: {date_str}</p>
                </div>
                
                <div class="content">
                    <div class="stat-card">
                        <div class="stat-label">⏱️ Session Duration</div>
                        <div class="stat-value">{duration} minutes</div>
                    </div>

                    <div class="stat-card">
                        <div class="stat-label">🎯 Total Queries</div>
                        <div class="stat-value">{total_queries}</div>
                    </div>

                    <div class="stat-card">
                        <div class="stat-label">📈 Average Confidence</div>
                        <div class="stat-value">{avg_confidence:.1f}%</div>
                    </div>

                    <div class="tool-section">
                        <div class="tool-label">🔧 Tools Used</div>
                        {tool_rows}
                    </div>

                    <div class="stat-card" style="border-left: 4px solid #ed8936;">
                        <div class="stat-label" style="color: #ed8936;">💬 Conversation Practice</div>
                        <p style="margin: 5px 0;">Total messages: <b>{total_queries}</b></p>
                        <p style="margin: 5px 0;">Corrections made: <b>0</b></p>
                    </div>

                    <h2 style="color: #667eea; margin-top: 30px;">Keep up the great work! 🌟</h2>
                    <p style="color: #718096;">You're making excellent progress in your English learning journey. Continue practicing regularly to improve your skills.</p>
                </div>

                <div class="footer">
                    <p><b>See you in the next session! 📚</b></p>
                    <p style="opacity: 0.7;">Powered by English Learning AI Agent</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html
