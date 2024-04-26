interface SearchProps {}

const Search: React.FunctionComponent<SearchProps> = ({}) => {
  return (
    <div className="border-base-300 relative flex h-full flex-grow items-center gap-4 rounded-lg border px-2">
      <div className="i-heroicons-magnifying-glass pointer-events-none absolute h-5 w-5 opacity-70" />
      <input
        className="bg-base-100 w-full py-1 pl-8 outline-none"
        placeholder="Search"
      />
    </div>
  )
}

export default Search
