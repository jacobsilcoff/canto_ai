"""
JavaScript logic for the interactive lesson player
"""

def get_javascript(json_payload: str) -> str:
    """Generate complete JavaScript for the player"""
    return f"""
        const slides = {json_payload};
        let currentIdx = 0;
        let currentAudio = null;
        let wsTeacher = null;
        let wsStudent = null;
        let mediaRecorder = null;
        let audioChunks = [];
        let autoPlayTimeout = null;
        let highlightTimeout = null;
        let studentRecordingBlob = null;

        // === HIGHLIGHTING SYSTEM ===
        window.highlightPair = (sIdx, cIdx, active) => {{
            const cantoId = `c_${{sIdx}}_${{cIdx}}`;
            const engId = `e_${{sIdx}}_${{cIdx}}`;
            
            const cEl = document.getElementById(cantoId);
            const eEl = document.getElementById(engId);
            
            if (cEl) {{
                if (active) {{
                    cEl.classList.add('active');
                }} else {{
                    cEl.classList.remove('active');
                }}
            }}
            
            if (eEl) {{
                if (active) {{
                    eEl.classList.add('active');
                }} else {{
                    eEl.classList.remove('active');
                }}
            }}
        }};

        // === RENDERING FUNCTIONS ===
        function renderCantoPills(chunks, sIdx, isInteractive) {{
            return chunks.map((c, cIdx) => {{
                const styleVars = `--active-color:${{c.color}}; --active-bg:${{c.color}}20; --active-shadow:${{c.color}}40;`;
                const style = `${{styleVars}} border-color:${{c.color}}30; color:${{c.color}};`;
                const mouseEvt = `onmouseenter="highlightPair('${{sIdx}}', ${{cIdx}}, true)" onmouseleave="highlightPair('${{sIdx}}', ${{cIdx}}, false)"`;
                const clickEvt = isInteractive && c.audio_b64 ? `onclick="playB64('${{c.audio_b64}}', null, ${{cIdx}}, ${{sIdx}})"` : '';
                
                return `<span id="c_${{sIdx}}_${{cIdx}}" class="chunk-pill" style="${{style}}" ${{mouseEvt}} ${{clickEvt}}>
                    <span class="canto-text">${{c.cantonese}}</span>
                    <span class="jyutping">${{c.jyutping}}</span>
                </span>`;
            }}).join('');
        }}

        function renderEnglishRow(chunks, sIdx) {{
            const pills = chunks.map((c, cIdx) => {{
                const vars = `--hl-text:${{c.color}}; --hl-bg:${{c.color}}20; --hl-border:${{c.color}}; --hl-shadow:${{c.color}}40;`;
                const mouseEvt = `onmouseenter="highlightPair('${{sIdx}}', ${{cIdx}}, true)" onmouseleave="highlightPair('${{sIdx}}', ${{cIdx}}, false)"`;
                
                return `<span id="e_${{sIdx}}_${{cIdx}}" class="eng-chunk" style="${{vars}}" ${{mouseEvt}}>
                    ${{c.english}}
                </span>`;
            }}).join('');
            
            return `<div class="eng-row">
                <span class="eng-label">Literal:</span>
                ${{pills}}
            </div>`;
        }}

        function renderNaturalRow(text) {{
            if (!text) return '';
            return `<div class="natural-row">
                <span class="natural-icon">💬</span>
                <span class="natural-text">${{text}}</span>
            </div>`;
        }}

        // === DIALOGUE RENDERING ===
        function renderDialogue(content) {{
            let html = '<div class="slide-enter" style="padding-bottom: 50px;">';
            
            if (slides[currentIdx].type === 'intro_dialogue') {{
                html += `<div style="text-align:center; margin-bottom:24px;">
                    <button class="btn-reveal" onclick="startDialogueAutoPlay()" style="background: var(--primary-color);">
                        ↻ Replay Conversation
                    </button>
                </div>`;
            }}
            
            content.items.forEach((sent, sIdx) => {{
                html += `<div class="dialogue-row" id="row_${{sIdx}}">
                    <div class="speaker-col">
                        <div class="speaker-label">${{sent.speaker}}</div>
                        <div class="spk-btn" onclick="playSentenceWithHighlight('${{sent.full_audio_b64}}', ${{JSON.stringify(sent.chunks)}}, ${{sIdx}})">🔊</div>
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
                if (autoPlayTimeout) clearTimeout(autoPlayTimeout);
                playDialogueSequence(content.items, 0);
            }};
            
            autoPlayTimeout = setTimeout(window.startDialogueAutoPlay, 500);
        }}

        // === QUIZ RENDERING ===
        function renderQuiz(content) {{
            let ctxHtml = content.context.map(c => 
                `<span style="margin-right:8px; opacity:0.6">${{c.cantonese}}</span>`
            ).join('');
            
            let html = `
            <div class="slide-enter">
                <div class="quiz-header">
                    <div class="quiz-context">${{ctxHtml}}</div>
                    <div class="quiz-prompt">
                        How do you say:
                        <span>"${{content.target_english}}"</span>
                    </div>
                </div>
                
                <div style="text-align:center; margin-bottom:24px;">
                    <button class="btn-rec" id="recBtn" onclick="toggleRecord()">
                        <span>🎤</span>
                        <span id="recText">Record Your Answer</span>
                    </button>
                </div>
                
                <div style="text-align:center;" id="revealArea">
                    <button class="btn-reveal" onclick="revealAnswer()">👁 Reveal Answer</button>
                </div>
                
                <div id="ansContainer" class="answer-container">
                    <div class="answer-box">
                        <div style="margin-bottom:16px;">
                            ${{renderCantoPills(content.target_pills, 0, true)}}
                        </div>
                        <div style="text-align:left">
                            ${{renderEnglishRow(content.target_pills, 0)}}
                            ${{renderNaturalRow(content.target_english)}}
                        </div>
                    </div>
                    
                    <div class="wave-box">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div class="wave-label" style="color:#ef4444; margin-bottom: 0;">You</div>
                            <button class="nav-btn" onclick="playStudentRecording()" style="padding: 6px 16px; font-size: 0.85em;">
                                ▶️ Play
                            </button>
                        </div>
                        <div id="ws-student"></div>
                    </div>
                    
                    <div class="wave-box" style="border-color:#93c5fd;">
                        <div class="wave-label" style="color:#2563eb">Teacher</div>
                        <div id="ws-teacher"></div>
                    </div>
                    
                    <div style="text-align:center; margin-top:20px;">
                        <button class="btn-reveal" onclick="playB64('${{content.audio_b64}}')" style="background: var(--primary-color);">
                            🔊 Replay Teacher
                        </button>
                    </div>
                </div>
            </div>`;
            
            document.getElementById('app').innerHTML = html;
            document.getElementById('app').scrollTop = 0;
            
            setTimeout(() => {{
                console.log('Initializing waveforms...');
                if (document.getElementById('ws-student')) {{
                    wsStudent = WaveSurfer.create({{
                        container: '#ws-student',
                        waveColor: '#fca5a5',
                        progressColor: '#ef4444',
                        height: 60,
                        barWidth: 2,
                        barGap: 1,
                        normalize: true,
                        backend: 'WebAudio',
                        interact: true,
                        cursorWidth: 2,
                        cursorColor: '#991b1b'
                    }});
                    
                    // Enable interaction after loading
                    wsStudent.on('ready', () => {{
                        console.log('Student waveform ready - click to play/seek');
                    }});
                    
                    // Click anywhere to seek and play
                    wsStudent.on('interaction', () => {{
                        if (!wsStudent.isPlaying()) {{
                            wsStudent.play();
                        }}
                    }});
                    
                    console.log('Student waveform created');
                }}
                if (document.getElementById('ws-teacher')) {{
                    wsTeacher = WaveSurfer.create({{
                        container: '#ws-teacher',
                        waveColor: '#93c5fd',
                        progressColor: '#2563eb',
                        height: 60,
                        barWidth: 2,
                        barGap: 1,
                        normalize: true,
                        backend: 'WebAudio'
                    }});
                    console.log('Teacher waveform created');
                }}
            }}, 100);
        }}

        // === AUDIO PLAYBACK WITH WORD HIGHLIGHTING ===
        function playB64(b64, onEnd, chunkIndex = null, rowIndex = null) {{
            if (currentAudio) {{
                currentAudio.pause();
                currentAudio = null;
            }}
            
            if (highlightTimeout) {{
                clearTimeout(highlightTimeout);
                highlightTimeout = null;
            }}
            
            if (!b64) {{
                if (onEnd) onEnd();
                return;
            }}
            
            const aud = new Audio("data:audio/mp3;base64," + b64);
            currentAudio = aud;
            aud.onended = onEnd;
            aud.play().catch(console.log);
            
            if (wsTeacher && document.getElementById('ws-teacher')) {{
                wsTeacher.load(aud.src);
                wsTeacher.play();
            }}
            
            // Highlight specific chunk if provided
            if (chunkIndex !== null && rowIndex !== null) {{
                const cantoId = `c_${{rowIndex}}_${{chunkIndex}}`;
                const engId = `e_${{rowIndex}}_${{chunkIndex}}`;
                
                setTimeout(() => {{
                    const cEl = document.getElementById(cantoId);
                    const eEl = document.getElementById(engId);
                    if (cEl) cEl.classList.add('active');
                    if (eEl) eEl.classList.add('active');
                    
                    aud.onended = () => {{
                        if (cEl) cEl.classList.remove('active');
                        if (eEl) eEl.classList.remove('active');
                        if (onEnd) onEnd();
                    }};
                }}, 50);
            }}
        }}
        
        // === SENTENCE AUDIO WITH WORD-BY-WORD HIGHLIGHTING ===
        function playSentenceWithHighlight(audioB64, chunks, rowIndex, onEnd) {{
            if (currentAudio) {{
                currentAudio.pause();
                currentAudio = null;
            }}
            
            const aud = new Audio("data:audio/mp3;base64," + audioB64);
            currentAudio = aud;
            
            // Calculate timing for each chunk (rough estimate)
            const duration = 2000; // Will be updated once audio loads
            aud.addEventListener('loadedmetadata', () => {{
                const actualDuration = aud.duration * 1000; // Convert to ms
                const timePerChunk = actualDuration / chunks.length;
                
                // Clear all highlights first
                chunks.forEach((_, idx) => {{
                    const cEl = document.getElementById(`c_${{rowIndex}}_${{idx}}`);
                    const eEl = document.getElementById(`e_${{rowIndex}}_${{idx}}`);
                    if (cEl) cEl.classList.remove('active');
                    if (eEl) eEl.classList.remove('active');
                }});
                
                // Highlight each chunk in sequence
                chunks.forEach((chunk, idx) => {{
                    setTimeout(() => {{
                        // Remove previous highlight
                        if (idx > 0) {{
                            const prevCEl = document.getElementById(`c_${{rowIndex}}_${{idx-1}}`);
                            const prevEEl = document.getElementById(`e_${{rowIndex}}_${{idx-1}}`);
                            if (prevCEl) prevCEl.classList.remove('active');
                            if (prevEEl) prevEEl.classList.remove('active');
                        }}
                        
                        // Add current highlight
                        const cEl = document.getElementById(`c_${{rowIndex}}_${{idx}}`);
                        const eEl = document.getElementById(`e_${{rowIndex}}_${{idx}}`);
                        if (cEl) cEl.classList.add('active');
                        if (eEl) eEl.classList.add('active');
                    }}, timePerChunk * idx);
                }});
            }});
            
            aud.onended = () => {{
                // Clear all highlights
                chunks.forEach((_, idx) => {{
                    const cEl = document.getElementById(`c_${{rowIndex}}_${{idx}}`);
                    const eEl = document.getElementById(`e_${{rowIndex}}_${{idx}}`);
                    if (cEl) cEl.classList.remove('active');
                    if (eEl) eEl.classList.remove('active');
                }});
                if (onEnd) onEnd();
            }};
            
            aud.play().catch(console.log);
            
            if (wsTeacher && document.getElementById('ws-teacher')) {{
                wsTeacher.load(aud.src);
                wsTeacher.play();
            }}
        }}

        // === AUTO-PLAY DIALOGUE ===
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
            if (activeRow) {{
                activeRow.classList.add('playing');
                scrollToCenter(activeRow);
            }}
            
            playB64(items[index].full_audio_b64, () => {{
                autoPlayTimeout = setTimeout(() => playDialogueSequence(items, index + 1), 800);
            }});
        }}

        // === RECORDING ===
        window.toggleRecord = async () => {{
            const btn = document.getElementById('recBtn');
            const txt = document.getElementById('recText');
            
            if (!mediaRecorder || mediaRecorder.state === "inactive") {{
                try {{
                    const stream = await navigator.mediaDevices.getUserMedia({{ 
                        audio: {{
                            echoCancellation: true,
                            noiseSuppression: true,
                            sampleRate: 44100
                        }}
                    }});
                    
                    mediaRecorder = new MediaRecorder(stream, {{
                        mimeType: 'audio/webm'
                    }});
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = e => {{
                        if (e.data.size > 0) {{
                            audioChunks.push(e.data);
                            console.log('Audio chunk received:', e.data.size, 'bytes');
                        }}
                    }};
                    
                    mediaRecorder.onstop = () => {{
                        console.log('Recording stopped, chunks:', audioChunks.length);
                        const blob = new Blob(audioChunks, {{ type: 'audio/webm' }});
                        console.log('Blob created:', blob.size, 'bytes');
                        studentRecordingBlob = blob;
                        
                        if (wsStudent && blob.size > 0) {{
                            console.log('Loading blob into waveform...');
                            wsStudent.loadBlob(blob);
                        }} else {{
                            console.error('No waveform or empty blob');
                        }}
                        
                        stream.getTracks().forEach(t => t.stop());
                    }};
                    
                    mediaRecorder.start();
                    console.log('Recording started');
                    btn.classList.add("recording");
                    txt.innerText = "Stop Recording";
                }} catch(e) {{
                    console.error('Microphone error:', e);
                    alert("Microphone Error: " + e.message + "\\n\\nPlease allow microphone access and try again.");
                }}
            }} else {{
                console.log('Stopping recording...');
                mediaRecorder.stop();
                btn.classList.remove("recording");
                txt.innerText = "Record Your Answer";
            }}
        }};

        window.playStudentRecording = () => {{
            if (wsStudent) {{
                wsStudent.play();
            }}
        }};

        window.revealAnswer = () => {{
            document.getElementById('revealArea').style.display = 'none';
            document.getElementById('ansContainer').classList.add('visible');
            setTimeout(() => {{
                document.getElementById('ansContainer').scrollIntoView({{ behavior: 'smooth' }});
            }}, 100);
            const content = slides[currentIdx].content;
            playSentenceWithHighlight(content.audio_b64, content.target_pills, 0);
        }};

        // === SLIDE NAVIGATION ===
        window.changeSlide = (delta) => {{
            if (autoPlayTimeout) clearTimeout(autoPlayTimeout);
            if (currentAudio) {{
                currentAudio.pause();
                currentAudio = null;
            }}
            
            const newIdx = currentIdx + delta;
            if (newIdx < 0 || newIdx >= slides.length) return;
            
            currentIdx = newIdx;
            
            const progEl = document.getElementById('progress');
            if (progEl) progEl.innerText = `${{currentIdx + 1}} / ${{slides.length}}`;
            
            const prevEl = document.getElementById('prevBtn');
            if (prevEl) prevEl.disabled = (currentIdx === 0);
            
            const nextEl = document.getElementById('nextBtn');
            if (nextEl) {{
                if (currentIdx === slides.length - 1) {{
                    nextEl.innerText = 'Finish ✓';
                    nextEl.onclick = () => {{
                        // Trigger completion by setting query param
                        window.parent.location.href = window.parent.location.pathname + '?completed=true';
                    }};
                }} else {{
                    nextEl.innerText = 'Next →';
                    nextEl.onclick = () => changeSlide(1);
                }}
            }}
            
            const s = slides[currentIdx];
            if (s.type === 'intro_dialogue' || s.type === 'analysis') {{
                renderDialogue(s.content);
            }} else {{
                renderQuiz(s.content);
            }}
        }};

        // Initialize
        changeSlide(0);
    """