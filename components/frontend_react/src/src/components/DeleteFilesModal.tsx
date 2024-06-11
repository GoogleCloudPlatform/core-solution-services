import Loading from "@/navigation/Loading"
import axios from "axios"
import { useFormikContext } from "formik"
import { useRouter } from "next/router"
import nookies from "nookies"
import { useState } from "react"

type IfileFormat = {
  fileName: string | null | undefined
  fileURL: string
  fieldName: string
}

interface IDeleteFilesModal {
  fileData: IfileFormat | null
  demoId?: string
  partnerId?: string
  modalClose?: Function
}

const DeleteFilesModal: React.FC<IDeleteFilesModal> = ({
  fileData,
  demoId,
  partnerId,
  modalClose,
}) => {
  const [modal, setModal] = useState(true)
  const [loading, setLoading] = useState(false)
  const { setFieldValue } = useFormikContext()
  const token = nookies.get().token
  const router = useRouter()
  const { id } = router.query

  if (!fileData) throw new Error("Missing supporting files")

  const handleDelete = async () => {
    setLoading(true)
    const requestURL =
      demoId !== undefined
        ? `${process.env.NEXT_PUBLIC_API_BASE_URL}/demos/${demoId}/deleteFile/?filePath=${fileData.fileURL}&type=${fileData.fieldName}`
        : `${process.env.NEXT_PUBLIC_API_BASE_URL}/partners/${partnerId}/deleteFile/?filePath=${fileData.fileURL}`

    await axios
      .delete(requestURL, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then((res) => {
        if (res.status === 200) {
          demoId
            ? setFieldValue(
                fileData.fieldName,
                res.data.demo[fileData.fieldName],
              )
            : setFieldValue(fileData.fieldName, "")
        }
      })
      .catch((error) => {
        console.error(error)
      })
      .finally(() => {
        setLoading(false)
        setModal(false)
        modalClose && modalClose(false)
        router.push(`/input/?id=${id}`, undefined, { shallow: true })
      })
  }

  return (
    <>
      <input
        type="checkbox"
        id="delete-confirm-modal"
        className="modal-toggle"
        checked={modal}
        readOnly
      />
      <div className="modal">
        <div className="modal-box">
          <h3 className="font-bold text-lg">Delete</h3>
          <p className="py-4">Are you sure you want to delete the file?</p>
          <p className="text-md font-normal">{fileData.fileName}</p>
          <div className="modal-action">
            {loading ? (
              <Loading />
            ) : (
              <button
                className="btn btn-error"
                type="button"
                onClick={() => {
                  handleDelete()
                }}
              >
                Delete
              </button>
            )}
            <button
              className="btn btn-outline"
              type="button"
              onClick={() => {
                setModal(false), modalClose && modalClose(false)
              }}
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

export default DeleteFilesModal
