import { useState, useEffect } from 'react';
import { Box, Modal, Typography, IconButton, Button } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close'; // Import the correct CloseIcon
import { Document, Page, pdfjs } from 'react-pdf';
import { getStorage, ref, getDownloadURL } from 'firebase/storage';
import React from 'react';

// Set worker URL for react-pdf
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;


interface DocumentModalProps {
    open: boolean;
    onClose: () => void;
    selectedFile: File | null;
    fileURL?: string | null; // New optional prop
}

const DocumentModal: React.FC<DocumentModalProps> = ({ open, onClose, selectedFile, fileURL: fileURLProp }) => {
    const [numPages, setNumPages] = useState<number | null>(null);
    const [pageNumber, setPageNumber] = useState(1);
    const [fileURL, setFileURL] = useState<string | null>(null);
    const [fileType, setFileType] = useState<string | null>(null);
    useEffect(() => {
        // Reset page number when a new file is selected
        setPageNumber(1);
    }, [selectedFile, fileURLProp]);
    
    useEffect(() => {
        const fetchFileURL = async () => {
            if (selectedFile instanceof File) {
                setFileURL(URL.createObjectURL(selectedFile));
                // Extract file extension and set file type
                const fileName = selectedFile.name;
                const fileExtension = fileName.slice((fileName.lastIndexOf(".") - 1 >>> 0) + 2); // More robust
                setFileType(fileExtension); // You'll need to define setFileType
            } else if (fileURLProp) {
                try {
                    const storage = getStorage();
                    const fileRef = ref(storage, fileURLProp);
                    const downloadURL = await getDownloadURL(fileRef);
                    setFileURL(downloadURL); // Try setting the download URL directly
            
                    // Extract file extension from downloadURL
                    const url = new URL(downloadURL);
                    const pathname = url.pathname;
                    const fileExtension = pathname.slice((pathname.lastIndexOf(".") - 1 >>> 0) + 2);
                    setFileType(fileExtension); // set file type
            
                } catch (error) {
                    console.error("Failed to fetch Firebase URL:", error);
                    setFileURL(null);
                    setFileType(null); // Also reset file type on error
                }
            } else {
                setFileURL(null);
                setFileType(null); // Ensure file type is also reset when no file
            }
        };
    
        fetchFileURL();
     }, [selectedFile, fileURLProp]);
    const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
        setNumPages(numPages);
    };

    if (!open || (!selectedFile && !fileURLProp)) {
        return null;
    }


    // Display an error message if the selected "file" isn't actually a file object
    // if (!selectedFile.url) {  // check if the file object has a url
    //     return (
    //         <Modal open={open} onClose={onClose}>
    //             <Box sx={{ /* ... your modal styles */ }}>
    //                 <Typography variant="body1" color="error">
    //                     Invalid file selected. Please choose a valid PDF file.
    //                 </Typography>
    //                 <Button onClick={onClose}>Close</Button>
    //             </Box>
    //         </Modal>
    //     );
    // }

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = event.target.files?.[0];
        if (selectedFile) {
            setFileURL(URL.createObjectURL(selectedFile));
            const fileName = selectedFile.name;
            const fileExtension = fileName.slice((fileName.lastIndexOf(".") - 1 >>> 0) + 2);
            setFileType(fileExtension);
        }
    }
    return (
        <Modal open={open} onClose={onClose}>
            <Box sx={{
                position: 'absolute',
                top: 0,
                left: 0,
                backgroundColor: "#333537",
                p: 4,
                width: '100%',
                height: '100%',
                overflowY: 'auto',
            }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="h6">{selectedFile && selectedFile.name ? selectedFile.name : "Document"}</Typography>
                    <Typography variant="h6">{fileURL ? fileURL : "Document"}</Typography>
                    <IconButton onClick={onClose} size="small" sx={{ backgroundColor: "#A8C7FA" }}>
                        <CloseIcon sx={{ color: "#062E6F" }} />
                    </IconButton>
                </Box>
               
               <div>
            {/* File input for selecting a file */}
            {/* <input type="file" onChange={handleFileChange} /> */}

            {/* Display the file URL */}
            {fileURL && (
                <div>
                    {/* <p>File URL: {fileURL}</p>
                    {fileType && <p>File Type: {fileType}</p>} */}
                    <Box sx={{ height: 'calc(85vh)', overflowY: 'auto' }}>
                        {['html', 'htm', 'jpg', 'jpeg', 'png', 'gif', 'pdf'].includes(fileType || '') ? (
                            <iframe src={fileURL} width="100%" height="100%" />
                        ) : fileURL ? (
                            <a href={fileURL} download={`file.${fileType}`}>
                                Download {fileType?.toUpperCase()} File
                            </a>
                        ) : null}
                    </Box>
                </div>
            )}

            {!fileURL && (
                <p>No file selected or URL available.</p>
            )}
        </div>

            </Box>
        </Modal>
    );
};

export default DocumentModal;