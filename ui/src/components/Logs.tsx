import { Log } from "../types/utils.d"
import { timeAgo } from "../utils/utils"
function colorCode (item: string) {
  if (['covenant bookmarks', 'mystic medals'].includes(item.toLowerCase()))
    return 'text-green-500'
  if (item === 'Error') {
    return 'text-red-500'
  }
  return ''
}
export function Logs({logs}: {logs: Log[]}) {
   return ( 
    <div className="overflow-x-auto overflow-y-hidden w-full" >
      <table className="table table-xs w-full">
        <thead className="">
          <tr>
            <th></th>
            <th>Item</th>
            <th>Run</th>
            <th>Seen</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((item, index) => (
            <tr key={item.id || index}>
              <th>{index + 1}</th>
              <td className={colorCode(item.name)}>{item.name}</td>
              <td>{item.run}</td>
              <td>{timeAgo(item.time)}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
          </tr>
        </tfoot>
      </table>
    </div>
  )
}
