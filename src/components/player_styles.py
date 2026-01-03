"""
CSS Styles for the lesson player
Modern, Mango-inspired design with dark mode support
"""

def get_styles(footer_style: str, container_padding: str) -> str:
    """Generate complete CSS for the player"""
    return f"""
        :root {{
            --primary-color: #3b82f6;
            --success-color: #10b981;
            --error-color: #ef4444;
            --text-primary: #1f2937;
            --text-secondary: #6b7280;
            --text-tertiary: #9ca3af;
            --bg-primary: transparent;
            --bg-card: #ffffff;
            --bg-hover: #f9fafb;
            --border-color: #e5e7eb;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                --text-primary: #f9fafb;
                --text-secondary: #d1d5db;
                --text-tertiary: #9ca3af;
                --bg-card: #1f2937;
                --bg-hover: #374151;
                --border-color: #4b5563;
                --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.5);
                --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.6);
                --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.7);
            }}
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html, body {{
            height: 100%;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            overflow: hidden;
        }}

        body {{
            display: flex;
            flex-direction: column;
        }}

        .scroll-viewport {{
            flex: 1;
            overflow-y: auto;
            overflow-x: hidden;
            width: 100%;
            max-width: 900px;
            margin: 0 auto;
            padding: 24px;
            padding-bottom: {container_padding};
            scroll-behavior: smooth;
        }}

        .scroll-viewport::-webkit-scrollbar {{
            width: 8px;
        }}

        .scroll-viewport::-webkit-scrollbar-track {{
            background: transparent;
        }}

        .scroll-viewport::-webkit-scrollbar-thumb {{
            background: var(--text-tertiary);
            border-radius: 4px;
        }}

        .scroll-viewport::-webkit-scrollbar-thumb:hover {{
            background: var(--text-secondary);
        }}

        /* === ANIMATIONS === */
        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes pulse {{
            0%, 100% {{
                box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
            }}
            50% {{
                box-shadow: 0 0 0 15px rgba(239, 68, 68, 0);
            }}
        }}

        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateX(-10px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}

        .slide-enter {{
            animation: fadeIn 0.5s ease-out;
        }}

        /* === CHUNK PILLS === */
        .chunk-pill {{
            display: inline-flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 12px 16px;
            margin: 6px;
            border-radius: 12px;
            cursor: pointer;
            border: 2px solid transparent;
            background: var(--bg-card);
            box-shadow: var(--shadow-sm);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            min-height: 48px;
            position: relative;
        }}

        .chunk-pill:hover {{
            transform: translateY(-3px);
            box-shadow: var(--shadow-lg);
        }}

        .chunk-pill.active {{
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 4px 16px var(--active-shadow);
            border-width: 3px;
        }}

        .canto-text {{
            font-size: 1.75em;
            font-weight: 700;
            line-height: 1.2;
            letter-spacing: -0.01em;
        }}

        .jyutping {{
            font-size: 0.875em;
            font-family: 'Courier New', monospace;
            color: var(--text-tertiary);
            opacity: 0;
            max-height: 0;
            margin-top: 0;
            overflow: hidden;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .chunk-pill:hover .jyutping,
        .chunk-pill.active .jyutping {{
            opacity: 1;
            max-height: 30px;
            margin-top: 6px;
        }}

        /* === ENGLISH TRANSLATIONS === */
        .eng-row {{
            margin-top: 16px;
            padding-top: 16px;
            border-top: 2px dashed var(--border-color);
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
        }}

        .eng-label {{
            font-size: 0.75em;
            text-transform: uppercase;
            color: var(--text-tertiary);
            font-weight: 700;
            letter-spacing: 0.1em;
            margin-right: 8px;
        }}

        .eng-chunk {{
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 0.95em;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.25s;
            border: 2px solid transparent;
            background: transparent;
        }}

        .eng-chunk:hover,
        .eng-chunk.active {{
            font-weight: 700;
            transform: translateY(-2px) scale(1.05);
            border-color: var(--hl-border);
            background-color: var(--hl-bg);
            color: var(--hl-text);
            box-shadow: 0 2px 8px var(--hl-shadow);
        }}

        /* === NATURAL TRANSLATION === */
        .natural-row {{
            margin-top: 16px;
            padding: 14px 16px;
            background: var(--bg-hover);
            border-radius: 10px;
            border-left: 4px solid var(--primary-color);
            display: flex;
            align-items: flex-start;
            gap: 12px;
        }}

        .natural-icon {{
            font-size: 1.25em;
            opacity: 0.6;
            flex-shrink: 0;
        }}

        .natural-text {{
            font-style: italic;
            line-height: 1.6;
            color: var(--text-secondary);
        }}

        /* === DIALOGUE ROWS === */
        .dialogue-row {{
            margin-bottom: 24px;
            background: var(--bg-card);
            padding: 24px;
            border-radius: 16px;
            border: 2px solid var(--border-color);
            display: flex;
            align-items: flex-start;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            animation: slideIn 0.4s ease-out;
        }}

        .dialogue-row.playing {{
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            transform: scale(1.01);
        }}

        .speaker-col {{
            width: 60px;
            text-align: center;
            margin-right: 20px;
            flex-shrink: 0;
        }}

        .speaker-label {{
            font-weight: 700;
            font-size: 0.875em;
            color: var(--text-tertiary);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .spk-btn {{
            background: linear-gradient(135deg, var(--primary-color), #2563eb);
            color: white;
            border-radius: 50%;
            width: 44px;
            height: 44px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            box-shadow: var(--shadow-sm);
            font-size: 1.25em;
        }}

        .spk-btn:hover {{
            transform: scale(1.1);
            box-shadow: var(--shadow-md);
        }}

        .spk-btn:active {{
            transform: scale(0.95);
        }}

        /* === QUIZ STYLES === */
        .quiz-header {{
            text-align: center;
            margin-bottom: 32px;
        }}

        .quiz-context {{
            color: var(--text-secondary);
            font-size: 1.1em;
            margin-bottom: 16px;
            font-weight: 500;
        }}

        .quiz-prompt {{
            font-size: 2em;
            font-weight: 800;
            margin-bottom: 24px;
            line-height: 1.3;
        }}

        .quiz-prompt span {{
            color: var(--primary-color);
            display: block;
            margin-top: 8px;
        }}

        .btn-rec {{
            background: var(--error-color);
            color: white;
            border: none;
            padding: 14px 32px;
            border-radius: 50px;
            font-weight: 700;
            font-size: 1.1em;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 0 auto;
            transition: all 0.2s;
            box-shadow: var(--shadow-md);
        }}

        .btn-rec:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }}

        .btn-rec.recording {{
            animation: pulse 1.5s infinite;
            background: #991b1b;
        }}

        .btn-reveal {{
            background: var(--success-color);
            color: white;
            border: none;
            padding: 14px 36px;
            border-radius: 50px;
            font-weight: 700;
            font-size: 1.1em;
            cursor: pointer;
            margin: 0 auto;
            transition: all 0.2s;
            box-shadow: var(--shadow-md);
        }}

        .btn-reveal:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
            background: #059669;
        }}

        .answer-container {{
            margin-top: 32px;
            display: none;
            animation: fadeIn 0.5s ease-out;
        }}

        .answer-container.visible {{
            display: block;
        }}

        .answer-box {{
            background: var(--bg-card);
            border: 2px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            text-align: center;
        }}

        .wave-box {{
            background: var(--bg-card);
            border-radius: 12px;
            border: 2px solid var(--border-color);
            padding: 16px;
            margin-bottom: 12px;
            min-height: 100px;
        }}

        .wave-label {{
            font-size: 0.75em;
            color: var(--text-tertiary);
            text-transform: uppercase;
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: 0.05em;
        }}

        #ws-student, #ws-teacher {{
            min-height: 60px;
        }}

        /* === FOOTER NAVIGATION === */
        .footer-nav {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: var(--bg-card);
            padding: 16px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
            box-shadow: 0 -4px 6px -1px rgba(0, 0, 0, 0.1);
            border-top: 2px solid var(--border-color);
            {footer_style}
        }}

        .nav-btn {{
            background: var(--bg-hover);
            color: var(--text-primary);
            border: 2px solid var(--border-color);
            padding: 12px 28px;
            border-radius: 10px;
            font-weight: 700;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .nav-btn:hover:not(:disabled) {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }}

        .nav-btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}

        .nav-btn-primary {{
            background: linear-gradient(135deg, var(--primary-color), #2563eb);
            color: white;
            border-color: transparent;
        }}

        .nav-btn-primary:hover:not(:disabled) {{
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
        }}

        .progress-text {{
            font-weight: 700;
            color: var(--text-secondary);
            font-family: 'Courier New', monospace;
            font-size: 1.1em;
        }}

        /* === RESPONSIVE === */
        @media (max-width: 640px) {{
            .scroll-viewport {{
                padding: 16px;
            }}

            .chunk-pill {{
                padding: 10px 12px;
                margin: 4px;
            }}

            .canto-text {{
                font-size: 1.5em;
            }}

            .quiz-prompt {{
                font-size: 1.5em;
            }}

            .dialogue-row {{
                padding: 16px;
            }}

            .speaker-col {{
                width: 50px;
                margin-right: 12px;
            }}
        }}
    """