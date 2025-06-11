enum ResourceType {
  Mystics = 'm',
  Skystones = 's',
  Gold = 'g',
  Bookmarks = 'b'
}

type Resources = Record<ResourceType, number>;

interface Log {
  id: number;
  name: string;
  run: number;
  time: string;
}

export { ResourceType, Resources, Log }