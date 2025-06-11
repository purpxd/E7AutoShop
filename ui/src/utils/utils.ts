type TimeUnit = 'second' | 'minute' | 'hour' | 'day' | 'week' | 'month' | 'year';
type TimeInterval = [TimeUnit, number];

export function timeAgo(timestamp: string): string {
    const date: Date = new Date(timestamp);
    const now: Date = new Date();
    const seconds: number = Math.floor((now.getTime() - date.getTime()) / 1000);
  
    const intervals: TimeInterval[] = [
      ['year', 31536000],
      ['month', 2592000],
      ['week', 604800],
      ['day', 86400],
      ['hour', 3600],
      ['minute', 60],
      ['second', 1]
    ];
  
    for (const [unit, secondsInUnit] of intervals) {
      const interval: number = Math.floor(seconds / secondsInUnit);
      if (interval >= 1) {
        return new Intl.RelativeTimeFormat('en', { style: 'long' })
          .format(-interval, unit as TimeUnit);
      }
    }
    
    return 'just now';
  }