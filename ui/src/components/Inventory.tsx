import skystone from '../assets/s.png'
import gold from '../assets/g.png'
import mystic from '../assets/m.png'
import bookmark from '../assets/b.png'
import { Resources , ResourceType } from '../types/utils.d'

export function Inventory({ inventory }: { inventory: Resources }) {
  return (
    <div className="border-solid rounded-xl w-full">
      <div className='flex flex-row items-center gap-5 justify-center'>
        <div className='flex flex-row items-center gap-2'>
          <img
            src={gold}
            alt=""
            className="w-10 h-10 object-contain"
          />
          <span className={inventory[ResourceType.Gold] > 0 ? 'text-red-500' : ''}>{inventory[ResourceType.Gold].toLocaleString()}</span>
        </div>
        <div className='flex flex-row items-center gap-2'>
          <img
            src={skystone}
            alt=""
            className="w-10 h-10 object-contain"
          />
          <span className={inventory[ResourceType.Skystones] > 0 ? 'text-red-500' : ''}>{inventory[ResourceType.Skystones].toLocaleString()}</span>
        </div>
        <div className='flex flex-row items-center gap-2'>
          <img
            src={mystic}
            alt=""
            className="w-10 h-10 object-contain"
          />
          <span className={inventory[ResourceType.Mystics] > 0 ? 'text-green-500' : ''}>{inventory[ResourceType.Mystics].toLocaleString()}</span>
        </div>
        <div className='flex flex-row items-center gap-2'>
          <img
            src={bookmark}
            alt=""
            className="w-10 h-10 object-contain"
          />
          <span className={inventory[ResourceType.Bookmarks] > 0 ? 'text-green-500' : ''}>{inventory[ResourceType.Bookmarks].toLocaleString()}</span>
        </div>
      </div>
    </div>
  )
}
