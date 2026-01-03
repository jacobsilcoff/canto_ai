import json
import streamlit.components.v1 as components
from utils import get_b64_audio


def render_mango_player(slides_data, key, srs_mode=False):
    colors = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#6366f1"]

    js_slides = []
    for slide in slides_data:
        slide_obj = {'type': slide['type'], 'content': {}}

        def process_chunks(chunk_list):
            processed = []
            for i, c in enumerate(chunk_list):
                col = c.get('color', colors[i % len(colors)])
                # Fix: Handle case where audio_rel_path is explicitly None in the dict
                path = c.get('audio_rel_path')

                processed.append({
                    "cantonese": c['cantonese'],
                    "jyutping": c['jyutping'],
                    "english": c['english'],
                    "audio_b64": get_b64_audio(path),
                    "color": col
                })
            return processed

        if slide['type'] in ['intro_dialogue', 'analysis']:
            items = []
            data_source = slide['data'] if isinstance(slide['data'], list) else [slide['data']]
            for line in data_source:
                items.append({
                    "speaker": line.get('speaker', 'A'),
                    "english_natural": line.get('english_natural', ''),
                    "full_audio_b64": get_b64_audio(line.get('audio_rel_path')),
                    "chunks": process_chunks(line['chunks'])
                })
            slide_obj['content']['items'] = items

        elif slide['type'] == 'quiz_recall':
            slide_obj['content']['target_pills'] = process_chunks(slide['target_chunks'])
            slide_obj['content']['target_english'] = slide['target_english']
            slide_obj['content']['context'] = [{"cantonese": c['cantonese']} for c in slide['context']]

            # Safe audio fetching for Quiz Target
            t_audio = slide.get('target_audio')
            if t_audio:
                slide_obj['content']['audio_b64'] = get_b64_audio(t_audio)
            else:
                # Fallback: try first chunk
                if slide_obj['content']['target_pills']:
                    slide_obj['content']['audio_b64'] = slide_obj['content']['target_pills'][0]['audio_b64']
                else:
                    slide_obj['content']['audio_b64'] = None

        js_slides.append(slide_obj)

    json_payload = json.dumps(js_slides)

    # Styles
    footer_style = "display:none !important;" if srs_mode else ""
    container_style = "padding-bottom: 20px;" if srs_mode else "padding-bottom: 100px;"

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/wavesurfer.js@7.5.3/dist/wavesurfer.min.js"></script>
        <style>
             :root {{
                 --bg-color: transparent;
                 --text-color: #1f2937;
                 --card-bg: white;
                 --card-border: #f3f4f6;
                 --sub-text: #6b7280;
                 --pill-bg: white;
                 --pill-shadow: rgba(0,0,0,0.05);
                 --active-border: #2563eb;
                 --speaker-bg: #eff6ff;
                 --speaker-text: #2563eb;
                 --footer-bg: #1f2937;
                 --footer-text: white;
                 --natural-bg: #f9fafb;
                 --natural-text: #374151;
             }}

             @media (prefers-color-scheme: dark) {{
                 :root {{
                     --text-color: #f3f4f6;
                     --card-bg: #262626;
                     --card-border: #404040;
                     --sub-text: #9ca3af;
                     --pill-bg: #333333;
                     --pill-shadow: rgba(0,0,0,0.5);
                     --active-border: #60a5fa;
                     --speaker-bg: #374151;
                     --speaker-text: #93c5fd;
                     --natural-bg: #1f1f1f;
                     --natural-text: #d1d5db;
                 }}
             }}

             html, body {{ height: 100%; margin: 0; padding: 0; overflow: hidden; }}
             body {{ 
                 font-family: 'Helvetica Neue', Arial, sans-serif; 
                 background: var(--bg-color); 
                 color: var(--text-color);
                 display: flex;
                 flex-direction: column;
             }}

             .scroll-viewport {{
                 flex: 1;
                 overflow-y: auto;
                 width: 100%;
                 max-width: 800px;
                 margin: 0 auto;
                 padding: 20px;
                 {container_style}
                 box-sizing: border-box;
                 scroll-behavior: smooth;
             }}
             .scroll-viewport::-webkit-scrollbar {{ width: 8px; }}
             .scroll-viewport::-webkit-scrollbar-track {{ background: transparent; }}
             .scroll-viewport::-webkit-scrollbar-thumb {{ background: rgba(156, 163, 175, 0.5); border-radius: 4px; }}

             /* ANIMATIONS */
             .slide-enter {{ animation: fadeIn 0.4s ease-out; }}
             @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

             /* PILLS */
             .chunk-pill {{ 
                 display: inline-flex; 
                 flex-direction: column; 
                 align-items: center;
                 justify-content: center;
                 padding: 8px 12px; margin: 4px; 
                 border-radius: 10px; cursor: pointer; 
                 border: 2px solid transparent; 
                 vertical-align: top; 
                 background: var(--pill-bg); 
                 box-shadow: 0 2px 4px var(--pill-shadow);
                 transition: all 0.2s ease;
                 min-height: 44px;
             }}
             .chunk-pill:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
             .chunk-pill.active {{ background-color: var(--active-bg) !important; border-color: var(--active-color) !important; }}

             .canto-text {{ font-size: 1.5em; font-weight: bold; display: block; line-height: 1.1; }}

             /* JYUTPING */
             .jyutping {{ 
                 font-size: 0.85em; 
                 font-family: monospace; 
                 color: var(--sub-text); 
                 display: block; 
                 opacity: 0; 
                 max-height: 0; 
                 margin-top: 0;
                 overflow: hidden;
                 transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); 
             }}
             .chunk-pill:hover .jyutping,
             .chunk-pill.active .jyutping {{
                 opacity: 1;
                 max-height: 24px; 
                 margin-top: 4px;
             }}

             /* ENGLISH PILLS */
             .eng-row {{ 
                 margin-top: 12px; 
                 padding-top: 12px; 
                 border-top: 1px dashed var(--card-border); 
                 display: flex; 
                 flex-wrap: wrap; 
                 gap: 8px; 
                 align-items: center;
             }}
             .eng-label {{
                 font-size: 0.75em;
                 text-transform: uppercase;
                 color: var(--sub-text);
                 font-weight: bold;
                 margin-right: 8px;
                 letter-spacing: 0.05em;
             }}
             .eng-chunk {{
                 padding: 4px 8px;
                 border-radius: 6px;
                 font-size: 0.95em;
                 color: var(--sub-text);
                 cursor: pointer;
                 transition: all 0.2s;
                 border-bottom: 2px solid transparent;
                 opacity: 0.8;
             }}
             .eng-chunk:hover, .eng-chunk.active {{
                 opacity: 1;
                 background-color: var(--hl-bg);
                 color: var(--hl-text);
                 border-bottom-color: var(--hl-border);
                 font-weight: 500;
             }}

             /* NATURAL TRANS */
             .natural-row {{
                 margin-top: 12px;
                 padding: 10px 12px;
                 background-color: var(--natural-bg);
                 border-radius: 8px;
                 font-size: 1em;
                 color: var(--natural-text);
                 display: flex;
                 align-items: flex-start;
                 gap: 10px;
             }}
             .natural-icon {{ opacity: 0.5; font-size: 1.1em; }}
             .natural-text {{ font-style: italic; line-height: 1.4; }}

             /* DIALOGUE ROWS */
             .dialogue-row {{ 
                 margin-bottom: 20px; 
                 background: var(--card-bg); 
                 padding: 20px; 
                 border-radius: 16px; 
                 border: 1px solid var(--card-border); 
                 display: flex; 
                 align-items: flex-start; 
                 transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
             }}
             .dialogue-row.playing {{ 
                 border-color: var(--active-border); 
                 box-shadow: 0 8px 20px rgba(37, 99, 235, 0.1); 
                 transform: scale(1.005);
             }}

             .speaker-col {{ width: 50px; text-align: center; margin-right: 15px; font-weight: bold; color: var(--sub-text); padding-top: 8px; flex-shrink: 0; }}
             .spk-btn {{ background: var(--speaker-bg); color: var(--speaker-text); border-radius: 50%; width: 36px; height: 36px; cursor: pointer; margin: 8px auto; display: flex; align-items: center; justify-content: center; transition: background 0.2s; }}
             .spk-btn:hover {{ background: var(--active-border); color: white; }}

             .footer-nav {{ 
                 position: absolute; bottom: 0; left: 0; right: 0;
                 background: var(--footer-bg); 
                 color: var(--footer-text);
                 padding: 15px 20px; 
                 display: flex; justify-content: space-between; align-items: center; 
                 z-index: 100; 
                 box-shadow: 0 -4px 10px rgba(0,0,0,0.2);
                 {footer_style}
             }}
             .nav-btn {{ 
                 background: #374151; color: white; border: 1px solid #4b5563; 
                 padding: 10px 24px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: all 0.2s; 
                 min-width: 90px;
             }}
             .nav-btn.primary {{ background: #3b82f6; border-color: #2563eb; }}

             /* QUIZ & WAVE STYLES */
             .quiz-header {{ text-align: center; margin-bottom: 20px; }}
             .quiz-context {{ color: var(--sub-text); font-size: 1.2em; margin-bottom: 10px; }}
             .quiz-prompt {{ font-size: 2em; font-weight: 800; margin-bottom: 20px; }}
             .btn-rec {{ background: #ef4444; color: white; border: none; padding: 12px 24px; border-radius: 30px; font-weight: bold; font-size: 1.1em; cursor: pointer; display: flex; align-items: center; gap: 8px; margin: 0 auto; }}
             .btn-rec.recording {{ animation: pulse 1.5s infinite; background: #991b1b; }}
             .btn-reveal {{ background: #10b981; color: white; border: none; padding: 12px 30px; border-radius: 30px; font-weight: bold; font-size: 1.1em; cursor: pointer; margin: 0 auto; }}
             .answer-container {{ margin-top: 20px; display: none; animation: fadeIn 0.5s; }}
             .answer-container.visible {{ display: block; }}
             .wave-box {{ background: var(--card-bg); border-radius: 12px; border: 1px solid var(--card-border); padding: 10px; margin-bottom: 10px; }}
             .wave-label {{ font-size: 0.75em; color: var(--sub-text); text-transform: uppercase; font-weight: bold; margin-bottom: 5px; }}

             @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }} 70% {{ box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }} }}
        </style>
    </head>
    <body>
        <div id="app" class="scroll-viewport"></div>

        <div class="footer-nav">
            <button id="prevBtn" class="nav-btn" onclick="changeSlide(-1)">Back</button>
            <div id="progress" style="font-weight:bold; color:#9ca3af; font-family: monospace;">1 / 1</div>
            <button id="nextBtn" class="nav-btn primary" onclick="changeSlide(1)">Next</button>
        </div>

        <script>
            const slides = {json_payload};
            let currentIdx = 0;
            let currentAudio = null;
            let wsTeacher = null;
            let wsStudent = null;
            let mediaRecorder = null;
            let audioChunks = [];
            let autoPlayTimeout = null;

            window.highlightPair = (sIdx, cIdx, active) => {{
                const cantoId = `c_${{sIdx}}_${{cIdx}}`;
                const engId = `e_${{sIdx}}_${{cIdx}}`;

                const cEl = document.getElementById(cantoId);
                const eEl = document.getElementById(engId);

                if(cEl) active ? cEl.classList.add('active') : cEl.classList.remove('active');
                if(eEl) active ? eEl.classList.add('active') : eEl.classList.remove('active');
            }};

            function renderCantoPills(chunks, sIdx, isInteractive) {{
                return chunks.map((c, cIdx) => {{
                    const styleVars = `--active-color:${{c.color}}; --active-bg:${{c.color}}15;`;
                    const style = `${{styleVars}} border-color:${{c.color}}30; color:${{c.color}};`;
                    const mouseEvt = `onmouseenter="highlightPair('${{sIdx}}', ${{cIdx}}, true)" onmouseleave="highlightPair('${{sIdx}}', ${{cIdx}}, false)"`;
                    const clickEvt = isInteractive ? `onclick="playB64('${{c.audio_b64}}')"` : '';

                    return `<span id="c_${{sIdx}}_${{cIdx}}" class="chunk-pill" style="${{style}}" ${{mouseEvt}} ${{clickEvt}}>
                                <span class="canto-text">${{c.cantonese}}</span>
                                <span class="jyutping">${{c.jyutping}}</span>
                            </span>`;
                }}).join('');
            }}

            function renderEnglishRow(chunks, sIdx) {{
                const pills = chunks.map((c, cIdx) => {{
                    const vars = `--hl-text:${{c.color}}; --hl-bg:${{c.color}}15; --hl-border:${{c.color}};`;
                    const mouseEvt = `onmouseenter="highlightPair('${{sIdx}}', ${{cIdx}}, true)" onmouseleave="highlightPair('${{sIdx}}', ${{cIdx}}, false)"`;

                    return `<span id="e_${{sIdx}}_${{cIdx}}" class="eng-chunk" style="${{vars}}" ${{mouseEvt}}>
                                ${{c.english}}
                            </span>`;
                }}).join('');
                return `<div class="eng-row"><span class="eng-label">Literal:</span>${{pills}}</div>`;
            }}

            function renderNaturalRow(text) {{
                if(!text) return '';
                return `<div class="natural-row">
                    <span class="natural-icon">💬</span>
                    <span class="natural-text">${{text}}</span>
                </div>`;
            }}

            function renderDialogue(content) {{
                let html = '<div class="slide-enter" style="padding-bottom: 50px;">';
                if(slides[currentIdx].type === 'intro_dialogue') {{
                     html += `<div style="text-align:center; margin-bottom:20px; color:var(--sub-text)">
                        <button class="nav-btn" onclick="startDialogueAutoPlay()">↻ Replay</button>
                     </div>`;
                }}

                content.items.forEach((sent, sIdx) => {{
                    html += `<div class="dialogue-row" id="row_${{sIdx}}">
                        <div class="speaker-col">
                            ${{sent.speaker}}
                            <div class="spk-btn" onclick="playB64('${{sent.full_audio_b64}}')">🔊</div>
                        </div>
                        <div style="flex-grow:1">
                            <div>${{renderCantoPills(sent.chunks, sIdx, true)}}</div>
                            ${{renderEnglishRow(sent.chunks, sIdx)}}
                            ${{renderNaturalRow(sent.english_natural)}}
                        </div>
                    </div>`;
                }});
                html += '</div>';
                document.getElementById('app').innerHTML = html;
                document.getElementById('app').scrollTop = 0;

                window.startDialogueAutoPlay = () => {{
                    if(autoPlayTimeout) clearTimeout(autoPlayTimeout);
                    playDialogueSequence(content.items, 0);
                }};
                autoPlayTimeout = setTimeout(window.startDialogueAutoPlay, 500);
            }}

            function playB64(b64, onEnd) {{
                if (currentAudio) {{ currentAudio.pause(); currentAudio = null; }}
                if (!b64) {{ if(onEnd) onEnd(); return; }}
                const aud = new Audio("data:audio/mp3;base64," + b64);
                currentAudio = aud;
                aud.onended = onEnd;
                aud.play().catch(console.log);
                if(wsTeacher && document.getElementById('ws-teacher')) {{ wsTeacher.load(aud.src); wsTeacher.play(); }}
            }}

            function scrollToCenter(el) {{
                const container = document.getElementById('app');
                const elRect = el.getBoundingClientRect();
                const containerRect = container.getBoundingClientRect();
                const relativeTop = elRect.top - containerRect.top;
                const target = container.scrollTop + relativeTop - (containerRect.height / 2) + (elRect.height / 2);
                container.scrollTo({{ top: target, behavior: 'smooth' }});
            }}

            function playDialogueSequence(items, index) {{
                if (index >= items.length) return;
                document.querySelectorAll('.dialogue-row').forEach(r => r.classList.remove('playing'));
                const activeRow = document.getElementById(`row_${{index}}`);
                if(activeRow) {{
                    activeRow.classList.add('playing');
                    scrollToCenter(activeRow);
                }}
                playB64(items[index].full_audio_b64, () => {{
                    autoPlayTimeout = setTimeout(() => playDialogueSequence(items, index + 1), 800);
                }});
            }}

            function renderQuiz(content) {{
                let ctxHtml = content.context.map(c => `<span style="margin-right:8px; opacity:0.6">${{c.cantonese}}</span>`).join('');
                let html = `
                <div class="slide-enter">
                    <div class="quiz-header">
                        <div class="quiz-context">${{ctxHtml}}</div>
                        <div class="quiz-prompt">How do you say:<br><span style="color:#2563eb">"${{content.target_english}}"</span>?</div>
                    </div>
                    <div style="text-align:center; margin-bottom:20px;">
                         <button class="btn-rec" id="recBtn" onclick="toggleRecord()"><span>🎤</span> <span id="recText">Record</span></button>
                    </div>
                    <div style="text-align:center;" id="revealArea">
                        <button class="btn-reveal" onclick="revealAnswer()">👁 Reveal</button>
                    </div>

                    <div id="ansContainer" class="answer-container">
                        <div style="background:var(--card-bg); border:1px solid var(--card-border); border-radius:12px; padding:15px; margin-bottom:20px; text-align:center;">
                             <div style="margin-bottom:10px;">${{renderCantoPills(content.target_pills, 0, true)}}</div>
                             <div style="text-align:left">
                                 ${{renderEnglishRow(content.target_pills, 0)}}
                                 ${{renderNaturalRow(content.target_english)}}
                             </div>
                        </div>

                        <div class="wave-box">
                            <div class="wave-label" style="color:#ef4444">You</div>
                            <div id="ws-student"></div>
                        </div>
                        <div class="wave-box" style="margin-top:5px; border-color:#93c5fd;">
                            <div class="wave-label" style="color:#2563eb">Teacher</div>
                            <div id="ws-teacher"></div>
                        </div>
                        <div style="text-align:center; margin-top:15px;">
                            <button class="nav-btn primary" onclick="playB64('${{content.audio_b64}}')">🔊 Replay Teacher</button>
                        </div>
                    </div>
                </div>`;
                document.getElementById('app').innerHTML = html;
                document.getElementById('app').scrollTop = 0;

                setTimeout(() => {{
                    if(document.getElementById('ws-student')) {{
                         wsStudent = WaveSurfer.create({{ container: '#ws-student', waveColor: '#fca5a5', progressColor: '#ef4444', height: 50, normalize: true }});
                    }}
                    if(document.getElementById('ws-teacher')) {{
                         wsTeacher = WaveSurfer.create({{ container: '#ws-teacher', waveColor: '#93c5fd', progressColor: '#2563eb', height: 50, normalize: true }});
                    }}
                }}, 50);
            }}

            window.toggleRecord = async () => {{
                const btn = document.getElementById('recBtn');
                const txt = document.getElementById('recText');
                if (!mediaRecorder || mediaRecorder.state === "inactive") {{
                    try {{
                        const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                        mediaRecorder = new MediaRecorder(stream);
                        audioChunks = [];
                        mediaRecorder.ondataavailable = e => {{ if(e.data.size > 0) audioChunks.push(e.data); }};
                        mediaRecorder.onstop = () => {{
                            const blob = new Blob(audioChunks, {{ type: 'audio/webm' }});
                            if(wsStudent) wsStudent.loadBlob(blob);
                            stream.getTracks().forEach(t => t.stop());
                        }};
                        mediaRecorder.start();
                        btn.classList.add("recording");
                        txt.innerText = "Stop";
                    }} catch(e) {{ alert("Mic Error: " + e.message); }}
                }} else {{
                    mediaRecorder.stop();
                    btn.classList.remove("recording");
                    txt.innerText = "Record";
                }}
            }};

            window.revealAnswer = () => {{
                document.getElementById('revealArea').style.display = 'none';
                document.getElementById('ansContainer').classList.add('visible');
                setTimeout(() => document.getElementById('ansContainer').scrollIntoView({{ behavior: 'smooth' }}), 100);
                playB64(slides[currentIdx].content.audio_b64);
            }};

            window.changeSlide = (delta) => {{
                if(autoPlayTimeout) clearTimeout(autoPlayTimeout);
                if(currentAudio) {{ currentAudio.pause(); currentAudio = null; }}

                const newIdx = currentIdx + delta;
                if(newIdx < 0 || newIdx >= slides.length) return;
                currentIdx = newIdx;

                const progEl = document.getElementById('progress');
                if(progEl) progEl.innerText = `${{currentIdx + 1}} / ${{slides.length}}`;

                const prevEl = document.getElementById('prevBtn');
                if(prevEl) prevEl.disabled = (currentIdx === 0);

                const nextEl = document.getElementById('nextBtn');
                if(nextEl) {{
                    nextEl.innerText = (currentIdx === slides.length - 1) ? "Finish" : "Next";
                    nextEl.onclick = (currentIdx === slides.length - 1) ? () => alert("Lesson Complete!") : () => changeSlide(1);
                }}

                const s = slides[currentIdx];
                if(s.type === 'intro_dialogue' || s.type === 'analysis') renderDialogue(s.content);
                else renderQuiz(s.content);
            }};

            changeSlide(0);
        </script>
    </body>
    </html>
    """
    height = 550 if srs_mode else 850
    components.html(html_code, height=height, scrolling=False)