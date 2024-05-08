// Copyright 2024 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the License);
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import {
  SortingState,
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table"
import React, { useEffect, useState } from "react"

interface TablesComponentProps {
  tableData: any
  tableHeaders: string[]
}

const TablesComponent: React.FC<TablesComponentProps> = ({
  tableData,
  tableHeaders,
}) => {
  //const navigate = useNavigate()
  // const { t } = useTranslation()

  const handleClick = (id: string) => () => {
    console.log(id)
  }

  const columnHelper = createColumnHelper<any>()

  const columns = tableHeaders.map((element) => {
    return columnHelper.accessor(element.toLowerCase(), {
      header: () => element,
      cell: (info) =>
        element.includes("ID") ? (
          <a
            className="link link-hover link-primary"
            onClick={handleClick(info.row.original)}
          >
            {info.getValue()}
          </a>
        ) : (
          <span>{info.renderValue()}</span>
        ),
      footer: (info) => info.column.id,
    })
  })

  // const columns = [
  //   columnHelper.accessor((row) => row.product, {
  //     id: "product",
  //     cell: (info) => (
  //       <a
  //         className="link link-primary link-hover"
  //         onClick={handleClick(info.row.original)}
  //       >
  //         {info.getValue()}
  //       </a>
  //     ),
  //     header: () => <span>Product</span>,
  //     footer: (info) => info.column.id,
  //   }),
  //   columnHelper.accessor("email", {
  //     header: () => "Email",
  //     cell: (info) => info.renderValue(),
  //     footer: (info) => info.column.id,
  //   }),
  //   columnHelper.accessor("date", {
  //     header: () => <span>Date</span>,
  //     footer: (info) => info.column.id,
  //   }),
  //   columnHelper.accessor("status", {
  //     header: () => <span>Status</span>,
  //     footer: (info) => info.column.id,
  //   }),
  // ]

  const [data, setData] = useState<Record<string, any>[]>([])
  const [sorting, setSorting] = useState<SortingState>([])

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
    },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  })

  useEffect(() => {
    setData(tableData)
  }, [tableData])

  return (
    <div className="bg-base-100 w-full">
      <table className="divide-base-200 border-base-200 table w-full divide-y rounded-md border">
        <thead className="bg-base-200">
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => {
                return (
                  <th
                    key={header.id}
                    colSpan={header.colSpan}
                    className="rounded-none"
                  >
                    {header.isPlaceholder ? null : (
                      <div
                        {...{
                          className: header.column.getCanSort()
                            ? "cursor-pointer select-none"
                            : "",
                          onClick: header.column.getToggleSortingHandler(),
                        }}
                      >
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext(),
                        )}
                        {{
                          asc: (
                            <span className="i-heroicons-arrow-up ml-1 inline-block h-3 w-3" />
                          ),
                          desc: (
                            <span className="i-heroicons-arrow-down ml-1 inline-block h-3 w-3" />
                          ),
                        }[header.column.getIsSorted() as string] ?? null}
                      </div>
                    )}
                  </th>
                )
              })}
            </tr>
          ))}
        </thead>
        <tbody className="divide-base-200 bg-base-100 divide-y-2">
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default TablesComponent
