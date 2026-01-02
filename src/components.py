import json
import streamlit.components.v1 as components
from utils import get_b64_audio


def render_mango_player(slide_data, key):
    """
    Injects the HTML/JS player into Streamlit.
    """
    colors = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#6366f1"]
    js_payload = {'type': slide_data['type'], 'items': []}

    # 1. DATA PREPARATION LOGIC
    if slide_data['type'] in ['intro_dialogue', 'analysis']:
        data_source = slide_data['data'] if isinstance(slide_data['data'], list) else [slide_data['data']]
        for s_idx, line in enumerate(data_source):
            sentence_chunks = []
            for c_idx, c in enumerate(line['chunks']):
                sentence_chunks.append({
                    "id": f"s{s_idx}_c{c_idx}",
                    "cantonese": c['cantonese'],
                    "jyutping": c['jyutping'],
                    "english": c['english'],
                    "audio_b64": get_b64_audio(c['audio_rel_path']),
                    "color": colors[c_idx % len(colors)]
                })
            js_payload['items'].append({
                "sentence_id": s_idx,
                "speaker": line.get('speaker', 'A'),
                "english_natural": line.get('english_natural', ''),
                "full_audio_b64": get_b64_audio(line['audio_rel_path']),
                "chunks": sentence_chunks
            })

    elif slide_data['type'] == 'quiz_recall':
        target = slide_data['target_chunk']
        js_payload['target'] = {
            "cantonese": target['cantonese'],
            "jyutping": target['jyutping'],
            "english": target['english'],
            "audio_b64": get_b64_audio(target['audio_rel_path']),
        }
        js_payload['context'] = [{"cantonese": c['cantonese']} for c in slide_data['context']]

    json_str = json.dumps(js_payload)

    # 2. THE HTML TEMPLATE
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
             body {{ font-family: 'Helvetica Neue', Arial, sans-serif; padding: 10px; display:flex; flex-direction:column; align-items:center; background: transparent; }}
             .container {{ width: 100%; max-width: 800px; padding-bottom: 100px; }}

             /* PILLS */
             .chunk-pill {{ display: inline-block; padding: 6px 10px; margin: 3px; border-radius: 6px; cursor: pointer; border: 2px solid transparent; transition: all 0.15s ease; vertical-align: top; }}
             .chunk-pill:hover {{ transform: scale(1.05); }}
             .chunk-pill.playing {{ background-color: #2563eb !important; color: white !important; transform: scale(1.05); }}
             .canto-text {{ font-size: 1.3em; font-weight: bold; display: block; }}
             .eng-text {{ font-size: 0.9em; font-weight: 500; display: block; }}
             .jyutping {{ font-size: 0.75em; font-family: monospace; color: #555; opacity: 0; height: 0; transition: opacity 0.2s; }}
             .chunk-pill:hover .jyutping, .chunk-pill.playing .jyutping {{ opacity: 1; height: auto; }}

             /* DIALOGUE */
             .dialogue-row {{ display: flex; margin-bottom: 25px; background: white; padding: 15px; border-radius: 12px; border: 1px solid #f3f4f6; align-items: flex-start; transition: box-shadow 0.3s; }}
             .dialogue-row.active-row {{ box-shadow: 0 0 0 2px #2563eb; }}
             .speaker-col {{ width: 50px; flex-shrink: 0; text-align: center; margin-right: 15px; }}
             .spk-btn {{ background: #eff6ff; border: 1px solid #bfdbfe; color: #2563eb; border-radius: 50%; width: 35px; height: 35px; cursor: pointer; margin: 5px auto; display: flex; align-items: center; justify-content: center; font-size: 1.2em; }}
             .spk-btn:hover {{ background: #2563eb; color: white; }}
             .content-stack {{ flex-grow: 1; }}
             .natural-trans {{ margin-top: 8px; color: #4b5563; font-style: italic; font-size: 0.95em; border-top: 1px dashed #e5e7eb; padding-top: 4px; }}

             /* QUIZ */
             .quiz-box {{ text-align: center; margin-top: 20px; width: 100%; }}
             .quiz-context {{ color: #9ca3af; font-size: 1.5em; margin-bottom: 30px; font-weight:bold; min-height: 40px; }}
             .quiz-prompt {{ font-size: 1.8em; font-weight: bold; color: #1f2937; margin-bottom: 30px; }}
             .answer-card {{ display: none; padding: 20px; background: #eff6ff; border-radius: 15px; border: 2px solid #bfdbfe; margin-top: 20px; cursor: pointer; }}
             .answer-card.visible {{ display: block; animation: fadeIn 0.5s; }}

             /* CONTROLS */
             .rec-controls {{ margin: 20px 0; display: flex; gap: 10px; justify-content: center; }}
             .btn {{ padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; border: none; }}
             .btn-rec {{ background: #ef4444; color: white; }}
             .btn-rec.recording {{ animation: pulse 1.5s infinite; background: #991b1b; }}
             .btn-play {{ background: #3b82f6; color: white; }}
             .btn-reveal {{ background: #10b981; color: white; font-size: 1.1em; }}

             @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} 100% {{ opacity: 1; }} }}
             @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        </style>
    </head>
    <body>
        <div id="app" class="container"></div>
        <script>
            const data = {json_str};
            const app = document.getElementById('app');
            let currentAudio = null;
            let mediaRecorder = null;
            let audioChunks = [];
            let userAudioBlob = null;
            let recordingStream = null;

            function playFrom(b64, onEnd) {{
                if(currentAudio) {{ currentAudio.pause(); currentAudio = null; }}
                if(!b64) {{ if(onEnd) onEnd(); return; }}
                const aud = new Audio("data:audio/mp3;base64," + b64);
                currentAudio = aud;
                aud.onended = onEnd;
                aud.play().catch(e => console.log("Playback error:", e));
            }}

            function playSequence(queue, index) {{
                if (index >= queue.length) {{
                    document.querySelectorAll('.chunk-pill').forEach(p => p.classList.remove('playing'));
                    document.querySelectorAll('.dialogue-row').forEach(r => r.classList.remove('active-row'));
                    return;
                }}
                const item = queue[index];
                if(item.domId) {{
                    document.querySelectorAll('.chunk-pill').forEach(p => p.classList.remove('playing'));
                    const el = document.getElementById(item.domId);
                    if(el) el.classList.add('playing');
                }}
                if(item.rowId) {{
                    document.querySelectorAll('.dialogue-row').forEach(r => r.classList.remove('active-row'));
                    const row = document.getElementById(item.rowId);
                    if(row) {{
                        row.classList.add('active-row');
                        row.scrollIntoView({{ behavior: "smooth", block: "center" }});
                    }}
                }}
                playFrom(item.audio, () => playSequence(queue, index + 1));
            }}

            async function toggleRecord(btn) {{
                if (!mediaRecorder || mediaRecorder.state === "inactive") {{
                    try {{
                        const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                        recordingStream = stream; // Keep ref to stop later

                        // Check supported types
                        let options = {{}};
                        if (MediaRecorder.isTypeSupported('audio/webm')) options.mimeType = 'audio/webm';
                        else if (MediaRecorder.isTypeSupported('audio/mp4')) options.mimeType = 'audio/mp4';

                        mediaRecorder = new MediaRecorder(stream, options);
                        audioChunks = [];

                        mediaRecorder.ondataavailable = e => {{
                            if (e.data.size > 0) audioChunks.push(e.data);
                        }};

                        mediaRecorder.onstop = () => {{
                            // Create blob with the actual recorded type
                            const blobType = mediaRecorder.mimeType || 'audio/webm';
                            userAudioBlob = new Blob(audioChunks, {{ type: blobType }});

                            // Stop all tracks to release mic
                            recordingStream.getTracks().forEach(track => track.stop());
                        }};

                        mediaRecorder.start();
                        btn.innerText = "⏹ Stop Recording";
                        btn.classList.add("recording");

                    }} catch(e) {{
                        console.error(e);
                        alert("Microphone error: " + e.message);
                    }}
                }} else {{
                    mediaRecorder.stop();
                    btn.innerText = "🎤 Record Answer";
                    btn.classList.remove("recording");
                }}
            }}

            function playUserAudio() {{
                if(userAudioBlob) {{
                    const url = URL.createObjectURL(userAudioBlob);
                    const aud = new Audio(url);
                    aud.play().catch(e => alert("Playback failed: " + e.message));
                }} else {{
                    alert("Please record something first!");
                }}
            }}

            function renderDialogue() {{
                data.items.forEach((sent, sIdx) => {{
                    const row = document.createElement('div');
                    row.className = 'dialogue-row';
                    row.id = `row_${{sIdx}}`;

                    const spkCol = document.createElement('div');
                    spkCol.className = 'speaker-col';
                    spkCol.innerHTML = `<div style="font-weight:bold;color:#aaa">${{sent.speaker}}</div>`;
                    const btn = document.createElement('div');
                    btn.className = 'spk-btn';
                    btn.innerHTML = '🔊';
                    btn.onclick = () => playFrom(sent.full_audio_b64);
                    spkCol.appendChild(btn);

                    const stack = document.createElement('div');
                    stack.className = 'content-stack';
                    const rowCanto = document.createElement('div');
                    const rowEng = document.createElement('div');

                    sent.chunks.forEach((chunk, cIdx) => {{
                        const domId = `s${{sIdx}}_c${{cIdx}}`;
                        const bgCol = chunk.color + '15';
                        const txtCol = chunk.color;
                        const pillStyle = `background-color:${{bgCol}}; color:${{txtCol}}; border-color:${{chunk.color}}30;`;

                        const handleClick = () => {{
                            const queue = [];
                            for(let i=cIdx; i<sent.chunks.length; i++) {{
                                queue.push({{ audio: sent.chunks[i].audio_b64, domId: `s${{sIdx}}_c${{i}}` }});
                            }}
                            for(let k=sIdx+1; k<data.items.length; k++) {{
                                queue.push({{ audio: data.items[k].full_audio_b64, domId: null, rowId: `row_${{k}}` }});
                            }}
                            playSequence(queue, 0);
                        }};

                        const cPill = document.createElement('span');
                        cPill.className = 'chunk-pill';
                        cPill.id = domId;
                        cPill.style.cssText = pillStyle;
                        cPill.innerHTML = `<span class="canto-text">${{chunk.cantonese}}</span><span class="jyutping">${{chunk.jyutping}}</span>`;
                        cPill.onclick = handleClick;
                        const ePill = document.createElement('span');
                        ePill.className = 'chunk-pill';
                        ePill.style.cssText = pillStyle;
                        ePill.innerHTML = `<span class="eng-text">${{chunk.english}}</span>`;
                        ePill.onclick = handleClick;

                        cPill.onmouseenter = () => ePill.style.borderColor = chunk.color;
                        cPill.onmouseleave = () => ePill.style.borderColor = chunk.color+'30';
                        ePill.onmouseenter = () => cPill.style.borderColor = chunk.color;
                        ePill.onmouseleave = () => cPill.style.borderColor = chunk.color+'30';

                        rowCanto.appendChild(cPill);
                        rowEng.appendChild(ePill);
                    }});
                    stack.appendChild(rowCanto);
                    stack.appendChild(rowEng);
                    if(sent.english_natural) {{
                        const nat = document.createElement('div');
                        nat.className = 'natural-trans';
                        nat.innerText = sent.english_natural;
                        stack.appendChild(nat);
                    }}
                    row.appendChild(spkCol);
                    row.appendChild(stack);
                    app.appendChild(row);
                }});
            }}

            function renderQuizRecall() {{
                const box = document.createElement('div');
                box.className = 'quiz-box';
                if(data.context) {{
                    const ctx = document.createElement('div');
                    ctx.className = 'quiz-context';
                    data.context.forEach(c => ctx.innerHTML += `<span style="margin-right:10px;">${{c.cantonese}}</span>`);
                    box.appendChild(ctx);
                }}
                const prompt = document.createElement('div');
                prompt.className = 'quiz-prompt';
                prompt.innerHTML = `How do you say:<br><span style="color:#2563eb">"${{data.target.english}}"</span>?`;
                box.appendChild(prompt);

                const ctrls = document.createElement('div');
                ctrls.className = 'rec-controls';
                const recBtn = document.createElement('button');
                recBtn.className = 'btn btn-rec';
                recBtn.innerText = '🎤 Record Answer';
                recBtn.onclick = () => toggleRecord(recBtn);
                const playBtn = document.createElement('button');
                playBtn.className = 'btn btn-play';
                playBtn.innerText = '▶ My Recording';
                playBtn.onclick = playUserAudio;
                ctrls.appendChild(recBtn);
                ctrls.appendChild(playBtn);
                box.appendChild(ctrls);

                const revealBtn = document.createElement('button');
                revealBtn.className = 'btn btn-reveal';
                revealBtn.innerText = '👁 Reveal Answer';
                const ans = document.createElement('div');
                ans.className = 'answer-card';
                ans.innerHTML = `
                    <div style="font-size:2.5em; font-weight:bold; color:#2563eb;">${{data.target.cantonese}}</div>
                    <div style="font-family:monospace; color:#6b7280;">${{data.target.jyutping}}</div>
                `;
                ans.onclick = () => playFrom(data.target.audio_b64);
                revealBtn.onclick = () => {{
                    ans.classList.add('visible');
                    revealBtn.style.display = 'none';
                    playFrom(data.target.audio_b64);
                }};
                box.appendChild(revealBtn);
                box.appendChild(ans);
                app.appendChild(box);
            }}

            if(data.type === 'intro_dialogue' || data.type === 'analysis') renderDialogue();
            else if(data.type === 'quiz_recall') renderQuizRecall();
        </script>
    </body>
    </html>
    """
    height = 600 if slide_data['type'] in ['intro_dialogue', 'analysis'] else 500
    components.html(html_code, height=height, scrolling=True)