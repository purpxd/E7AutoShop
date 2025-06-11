import { useState, useEffect } from 'react';

export function Timer({ isRunning, isPaused, command }: { isRunning: boolean, isPaused: boolean, command: string }) {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    let interval = null;

    if (isRunning && !isPaused) {
      interval = setInterval(() => {
        setSeconds(prevSeconds => prevSeconds + 1);
      }, 1000);
    }
    if (command === "start") {
      setSeconds(0)
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isRunning, isPaused, command]);

  const pulse = () => {
    if (isRunning && !isPaused) {
      return false
    } else if (isRunning && isPaused) {
      return true
    } else {
      return false
    }
  }

  const formatTimeValue = (value: number) => {
    return value.toString().padStart(2, '0');
  };

  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="text-4xl font-mono flex items-center"
        style={pulse() ? { animation: 'color-pulse 2s ease-in-out infinite' } : {}}
      >
        <div className="">
          {formatTimeValue(hours)}
        </div>
        <span className="mx-1 text-xl">:</span>
        <div className="">
          {formatTimeValue(minutes)}
        </div>
        <span className="mx-1 text-xl">:</span>
        <div className="">
          {formatTimeValue(secs)}
        </div>
      </div>
    </div>
  );
}
