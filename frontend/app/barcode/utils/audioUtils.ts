/**
 * Audio utility functions for barcode detection feedback
 */

/**
 * Plays a 800Hz beep sound to indicate barcode detection.
 *
 * FLOW:
 * 1. Creates Web Audio API context
 * 2. Creates oscillator and gain nodes
 * 3. Plays 800Hz sine wave beep for 100ms with fade-out
 */
export const playDetectionSound = () => {
  try {
    const AudioContextClass =
      window.AudioContext ||
      (window as unknown as { webkitAudioContext: typeof AudioContext })
        .webkitAudioContext;
    const audioContext = new AudioContextClass();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.frequency.value = 800; // 800 Hz beep
    oscillator.type = 'sine';

    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(
      0.01,
      audioContext.currentTime + 0.1
    );

    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.1);
  } catch (err) {
    console.error('Failed to play detection sound:', err);
  }
};
