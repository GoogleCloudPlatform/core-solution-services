interface FileListDisplay {
  label: string
  value: string
}

const FileListDisplay: React.FC<FileListDisplay> = ({ label, value }) => {
  return (
    <div className="w-full">
      <span className="mr-2 font-semibold capitalize">{label}</span>
      {value}
    </div>
  )
}

export default FileListDisplay
