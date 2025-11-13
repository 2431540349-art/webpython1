(function () {
  // recognizer.js - Attach speech + media recorder behaviors to .recorder elements
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;

  function log(...args) { console.log('[recognizer]', ...args); }

  function compareTexts(spoken, sample) {
    const normalize = text => (text || '').toLowerCase().replace(/[.,!?();:\\"'`–—]/g, '').trim();
    const spokenWords = normalize(spoken).split(/\s+/).filter(Boolean);
    const sampleWords = normalize(sample).split(/\s+/).filter(Boolean);

    if (sampleWords.length === 0) return { score: 0, matches: 0, total: 0 };

    let matches = 0;
    const sampleSet = new Set(sampleWords);
    spokenWords.forEach(w => { if (sampleSet.has(w)) matches++; });

    const lengthScore = Math.min(spokenWords.length, sampleWords.length) / Math.max(spokenWords.length || 1, sampleWords.length);
    const matchScore = matches / sampleWords.length;
    const totalScore = (lengthScore * 0.3 + matchScore * 0.7) * 100;
    return { score: Math.round(totalScore), matches, total: sampleWords.length };
  }

  // Levenshtein distance for character-level similarity
  function levenshtein(a, b) {
    if (a === b) return 0;
    const al = a.length, bl = b.length;
    if (al === 0) return bl;
    if (bl === 0) return al;
    let v0 = new Array(bl + 1), v1 = new Array(bl + 1);
    for (let i = 0; i <= bl; i++) v0[i] = i;
    for (let i = 0; i < al; i++) {
      v1[0] = i + 1;
      for (let j = 0; j < bl; j++) {
        const cost = a[i] === b[j] ? 0 : 1;
        v1[j + 1] = Math.min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost);
      }
      for (let k = 0; k <= bl; k++) v0[k] = v1[k];
    }
    return v1[bl];
  }

  function charSimilarityScore(spoken, sample) {
    // Normalize both strings - remove punctuation, extra spaces, and convert to lowercase
    const normalize = s => (s || '').toLowerCase()
      .replace(/[.,!?();:\\"'`–—]/g, '') // remove punctuation
      .replace(/\s+/g, ' ')              // normalize spaces
      .trim();
    
    const as = normalize(spoken);
    const bs = normalize(sample);
    
    console.log('[recognizer] Comparing texts:');
    console.log('Spoken (normalized):', as);
    console.log('Sample (normalized):', bs);
    
    if (!bs.length) return 0;
    
    const dist = levenshtein(as, bs);
    const maxLen = Math.max(as.length, bs.length);
    
    if (maxLen === 0) return 0;
    
    // Calculate similarity percentage
    const sim = Math.max(0, 1 - dist / maxLen);
    const score = Math.round(sim * 100);
    
    console.log('[recognizer] Levenshtein distance:', dist);
    console.log('[recognizer] Similarity score:', score);
    
    return score;
  }

  function initRecorder(rec) {
    const qid = rec.dataset.qid;
    const sampleText = rec.dataset.sample || '';
  // Safely parse autoWeight (allow 0 value)
  let autoWeight = Number(rec.dataset.autoWeight);
  if (!isFinite(autoWeight)) autoWeight = 0.7;
    const lang = rec.dataset.lang || 'en-US';

    const startBtn = rec.querySelector('.start-rec');
    const stopBtn = rec.querySelector('.stop-rec');
    const gradeBtn = rec.querySelector('.grade-speech');
    const status = rec.querySelector('.rec-status');
    const accuracy = rec.querySelector('.accuracy');
    const transcript = rec.querySelector('.transcript');
    const hidden = rec.querySelector('.speaking-input');
    const scoreInput = rec.querySelector('.speaking-score-input');

    if (!startBtn || !stopBtn || !hidden) {
      log('missing UI elements for recorder', qid);
      return;
    }

    if (!SpeechRec) {
      status.textContent = 'Trình duyệt không hỗ trợ SpeechRecognition (dùng Chrome/Edge).';
      startBtn.disabled = true;
      return;
    }

    let recognition = new SpeechRec();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = lang;

  let finalTranscript = '';
  let lastInterim = '';
    let mediaRecorder = null;
    let audioChunks = [];

    recognition.onresult = (event) => {
      let interim = '';
      console.log('[recognizer] Speech result event:', event);
      
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
          console.log('[recognizer] Final transcript:', finalTranscript, 'Confidence:', event.results[i][0].confidence);
        } else {
          interim += event.results[i][0].transcript;
          console.log('[recognizer] Interim transcript:', interim);
        }
      }
      // store last interim so grading can use it even if finalTranscript is empty
      lastInterim = interim;
      
      const combinedText = (finalTranscript || '') + ' ' + (interim || '');
      console.log('[recognizer] Combined text:', combinedText);
      
      // Store the current state in the hidden input for grading
      hidden.value = combinedText;
      transcript.innerHTML = '<div style="color:#0f172a">' + (finalTranscript || '') + '</div>' + (interim ? '<div style="color:#64748b">' + interim + '</div>' : '');
    };

    recognition.onerror = (event) => {
      console.error('recognition error', event);
      if (event.error === 'not-allowed') {
        status.textContent = 'Cần cấp quyền microphone';
      } else if (event.error === 'no-speech') {
        status.textContent = 'Không nghe thấy giọng nói';
      } else if (event.error === 'audio-capture') {
        status.textContent = 'Không tìm thấy microphone';
      } else {
        status.textContent = 'Lỗi thu âm: ' + event.error;
      }
      startBtn.disabled = false;
      stopBtn.disabled = true;
      if (gradeBtn) gradeBtn.style.display = 'none';
    };

    recognition.onend = () => {
      log('recognition ended for', qid);
      status.textContent = 'Đã dừng thu âm';
      startBtn.disabled = false;
      stopBtn.disabled = true;
      if (gradeBtn) gradeBtn.style.display = 'inline-block';
    };

    function gradeSpeech() {
      console.log('[recognizer] grade clicked for', qid);
      console.log('[recognizer] Sample text:', sampleText);
      
      // Get the transcript from the hidden input which has been continuously updated
      const combined = (hidden.value || '').trim();
      console.log('[recognizer] Current transcript to grade:', combined);
      
      if (!sampleText) {
        status.textContent = 'Không có câu mẫu để chấm';
        console.warn('[recognizer] missing sampleText for', qid);
        return;
      }
      if (!combined) {
        status.textContent = 'Không nghe được giọng nói - vui lòng kiểm tra: \n1. Micro có hoạt động không?\n2. Âm lượng có đủ lớn không?\n3. Bạn đã bấm "Bắt đầu đọc" trước khi nói chưa?';
        console.warn('[recognizer] empty transcript for', qid, 'value=', hidden.value);
        return;
      }
      // Character-level similarity score (0-100)
      const charScore = charSimilarityScore(combined, sampleText);
      const color = charScore >= 80 ? '#15803d' : charScore >= 60 ? '#ca8a04' : '#dc2626';
      // Show both numeric score and a visual progress bar (0-100)
      accuracy.innerHTML = '\n        <div style="color:' + color + '; font-weight:700">Điểm (0-100): ' + charScore + '</div>' +
        '<div style="margin-top:6px; width:160px; background:#e6e6e6; border-radius:6px; height:12px; overflow:hidden">' +
          '<div style="width:' + charScore + '%; background:' + color + '; height:100%"></div>' +
        '</div>' +
        '<div style="font-size:0.85em;color:#64748b;margin-top:6px">(So sánh ký tự với câu mẫu)</div>';
      if (scoreInput) {
        scoreInput.value = charScore;
        console.log('[recognizer] charScore written to input for', qid, charScore);
      } else {
        console.warn('[recognizer] no score input for', qid);
      }
    }

    // Advanced audio analysis utility
    function getAudioLevels(analyser, dataArray) {
      analyser.getByteFrequencyData(dataArray);
      
      // Get different frequency ranges
      const bass = dataArray.slice(0, 8).reduce((a, b) => a + b) / 8;
      const mid = dataArray.slice(8, 24).reduce((a, b) => a + b) / 16;
      const treble = dataArray.slice(24).reduce((a, b) => a + b) / (dataArray.length - 24);
      
      // Weight the frequencies for speech (emphasize mid-range)
      const weightedAvg = (bass * 0.2 + mid * 0.6 + treble * 0.2) / 256;
      return weightedAvg;
    }

    startBtn.addEventListener('click', async function () {
      try {
        console.log('[recognizer] Starting new recording session');
        finalTranscript = '';
        lastInterim = '';
        hidden.value = '';
        transcript.textContent = '';
        accuracy.textContent = '';
        audioChunks = [];
        if (gradeBtn) gradeBtn.style.display = 'none';

        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Set up enhanced audio analysis
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioContext.createMediaStreamSource(stream);
        const analyser = audioContext.createAnalyser();
        
        // Increase precision of frequency analysis
        analyser.fftSize = 2048;
        analyser.smoothingTimeConstant = 0.8;
        
        source.connect(analyser);
        
        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        const volumeMeter = rec.querySelector('.volume-meter');
        const volumeLevel = volumeMeter.querySelector('.level');
        
        // Start volume meter animation
        volumeMeter.classList.add('active');
        let lastLevel = 0;
        let animationFrame;
        
        function updateVolume() {
          const instantLevel = getAudioLevels(analyser, dataArray);
          // Smooth out the visualization with some easing
          const smoothedLevel = lastLevel * 0.7 + instantLevel * 0.3;
          // Add extra boost to make the meter more responsive
          const boostedLevel = Math.pow(smoothedLevel, 0.8) * 150;
          // Ensure we don't exceed 100%
          const finalLevel = Math.min(100, boostedLevel);
          
          volumeLevel.style.width = finalLevel + '%';
          
          // Store for next frame
          lastLevel = smoothedLevel;
          animationFrame = requestAnimationFrame(updateVolume);
        }
        updateVolume();

        // Set up media recorder
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
        mediaRecorder.onstop = () => {
          const blob = new Blob(audioChunks, { type: 'audio/webm' });
          const reader = new FileReader();
          reader.onloadend = () => { if (hidden) hidden.value = reader.result; };
          reader.readAsDataURL(blob);
          
          // Clean up audio analysis
          cancelAnimationFrame(animationFrame);
          volumeMeter.classList.remove('active');
          volumeLevel.style.width = '0%';
          audioContext.close();
        };
        mediaRecorder.start();

        recognition.start();
        startBtn.disabled = true;
        stopBtn.disabled = false;
        status.textContent = 'Đang thu âm...';
        log('recording started', qid);
      } catch (err) {
        console.error('getUserMedia error', err);
        status.textContent = 'Không thể truy cập microphone: ' + (err && err.message ? err.message : err);
      }
    });

    stopBtn.addEventListener('click', function () {
      try {
        recognition.stop();
      } catch (e) { log('recognition stop err', e); }
      try {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
          mediaRecorder.stop();
          if (mediaRecorder.stream) mediaRecorder.stream.getTracks().forEach(t => t.stop());
        }
      } catch (e) { log('mediaRecorder stop err', e); }
      log('recording stopped', qid);
    });

    if (gradeBtn) gradeBtn.addEventListener('click', gradeSpeech);
  }

  function initAll() {
    document.querySelectorAll('.recorder').forEach(r => initRecorder(r));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
  } else {
    initAll();
  }
})();
