import { useCallback, useEffect, useRef, useState } from "react";

export const PLAYBACK_SPEEDS = [0.5, 1, 2, 5, 10] as const;

interface Args {
  frameCount: number;
  gridStepSeconds: number;
}

/** Drives replay playback via requestAnimationFrame, mapping elapsed
 * wall-clock time (scaled by the speed multiplier) onto a virtual replay
 * clock. Scrubbing/seeking just sets that virtual clock directly - both
 * paths converge on the same `currentTime` state, so every consumer
 * (car positions, leaderboard, telemetry panel) stays in sync regardless
 * of how the clock moved.
 *
 * Deliberately has no "reset when the race changes" effect: the caller
 * (ReplayViewer) is mounted with `key={sessionKey}`, so a new race simply
 * remounts this hook with fresh state instead of needing to reset it. */
export function useReplayClock({ frameCount, gridStepSeconds }: Args) {
  const totalDuration = Math.max((frameCount - 1) * gridStepSeconds, 0);

  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState<number>(1);

  const rafRef = useRef<number | null>(null);
  const lastTickRef = useRef<number | null>(null);

  useEffect(() => {
    if (!isPlaying) {
      lastTickRef.current = null;
      return;
    }

    function tick(now: number) {
      if (lastTickRef.current === null) {
        lastTickRef.current = now;
      }
      const deltaSeconds = ((now - lastTickRef.current) / 1000) * speed;
      lastTickRef.current = now;

      setCurrentTime((prev) => {
        const next = prev + deltaSeconds;
        if (next >= totalDuration) {
          setIsPlaying(false);
          return totalDuration;
        }
        return next;
      });

      rafRef.current = requestAnimationFrame(tick);
    }

    rafRef.current = requestAnimationFrame(tick);
    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    };
  }, [isPlaying, speed, totalDuration]);

  const play = useCallback(() => {
    if (totalDuration <= 0) return;
    setCurrentTime((t) => (t >= totalDuration ? 0 : t));
    setIsPlaying(true);
  }, [totalDuration]);

  const pause = useCallback(() => setIsPlaying(false), []);

  const toggle = useCallback(() => {
    setIsPlaying((p) => {
      if (!p && totalDuration <= 0) return p;
      return !p;
    });
  }, [totalDuration]);

  const restart = useCallback(() => {
    setCurrentTime(0);
    setIsPlaying(false);
  }, []);

  const seek = useCallback(
    (time: number) => {
      setCurrentTime(Math.min(Math.max(time, 0), totalDuration));
    },
    [totalDuration],
  );

  const frameIndexFloat = gridStepSeconds > 0 ? currentTime / gridStepSeconds : 0;
  const frameIndex = Math.min(Math.floor(frameIndexFloat), Math.max(frameCount - 1, 0));
  const frameFraction = frameIndexFloat - frameIndex;

  return {
    currentTime,
    frameIndex,
    frameFraction,
    isPlaying,
    speed,
    totalDuration,
    play,
    pause,
    toggle,
    restart,
    seek,
    setSpeed,
  };
}
