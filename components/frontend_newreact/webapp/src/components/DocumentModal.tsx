import { useState, useEffect } from 'react';
import { Box, Modal, Typography, IconButton, Button } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close'; // Import the correct CloseIcon
import { Document, Page, pdfjs } from 'react-pdf';

// Set worker URL for react-pdf
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;


interface DocumentModalProps {
    open: boolean;
    onClose: () => void;
    selectedFile: File | null;
}

const DocumentModal: React.FC<DocumentModalProps> = ({ open, onClose, selectedFile }) => {
    const [numPages, setNumPages] = useState<number | null>(null);
    const [pageNumber, setPageNumber] = useState(1);

    useEffect(() => {
        // Reset page number when a new file is selected
        setPageNumber(1);
    }, [selectedFile]);

    const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
        setNumPages(numPages);
    };

    if (!open || !selectedFile) {
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
                    <Typography variant="h6">{selectedFile.name}</Typography>
                    <IconButton onClick={onClose} size="small" sx={{ backgroundColor: "#A8C7FA" }}>
                        <CloseIcon sx={{ color: "#062E6F" }} />
                    </IconButton>
                </Box>
                {/* Paper wrapper for the PDF document (you can remove this if not needed) */}
                {/* <Box sx={{ height: 'calc(80vh)', overflowY: 'auto' }}>
                    <Document file={selectedFile} onLoadSuccess={onDocumentLoadSuccess}>
                        {Array.from(new Array(numPages), (el, index) => (  // Render all pages
                            <Page key={`page_${index + 1}`} pageNumber={index + 1} />
                        ))}
                    </Document>
                </Box> */}
                <Box sx={{ height: 'calc(85vh)', overflowY: 'auto' }}>
                    <iframe src={URL.createObjectURL(selectedFile)} width="100%" height={"100%"}></iframe>
                </Box>

            </Box>
        </Modal>
    );
};

export default DocumentModal;