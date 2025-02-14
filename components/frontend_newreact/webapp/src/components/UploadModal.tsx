import { Box, Typography, IconButton, Button, TextField, Divider } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import DeleteIcon from '@mui/icons-material/Delete';
import FileUploadIcon from '@mui/icons-material/FileUpload';

export interface FileUpload {
  name: string;
  progress?: number;
  error?: string;
}

interface UploadModalProps {
  open: boolean;
  onClose: () => void;
  uploadedFiles: FileUpload[];
  onFileSelect: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onRemoveFile: (fileName: string) => void;
  importUrl: string;
  onImportUrlChange: (url: string) => void;
  onAdd: () => void;
}

const UploadModal: React.FC<UploadModalProps> = ({
  open,
  onClose,
  uploadedFiles,
  onFileSelect,
  onRemoveFile,
  importUrl,
  onImportUrlChange,
  onAdd,
}) => {
  return (
    <Box className="upload-modal">
      <Box className="upload-modal-header">
        <Typography variant="h6" id="upload-modal-title">Add Files</Typography>
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </Box>

      <Box className="upload-area">
        <input
          type="file"
          id="file-upload"
          multiple
          hidden
          onChange={onFileSelect}
        />
        <label htmlFor="file-upload" className="upload-drop-zone">
          <FileUploadIcon />
          <Typography>
            Drag & drop or <span className="choose-file-text">choose a file</span> to upload
          </Typography>
        </label>
      </Box>

      {uploadedFiles.map((file) => (
        <Box key={file.name} className="uploaded-file">
          <Box className="file-info">
            <Typography>{file.name}</Typography>
            {file.error ? (
              <Typography color="error">There was an issue uploading {file.name}</Typography>
            ) : (
              <Box className="upload-progress">
                <Box className="progress-bar" style={{ width: `${file.progress}%` }} />
              </Box>
            )}
          </Box>
          <IconButton onClick={() => onRemoveFile(file.name)} size="small">
            <DeleteIcon />
          </IconButton>
        </Box>
      ))}

      <Divider sx={{ my: 2 }}>or</Divider>

      <Box className="import-url-section">
        <Typography variant="subtitle2">Import from URL</Typography>
        <TextField
          fullWidth
          placeholder="http(s)://, gs://, shpt://"
          value={importUrl}
          onChange={(e) => onImportUrlChange(e.target.value)}
          variant="outlined"
          size="small"
          sx={{
            '& .MuiOutlinedInput-root': { // Target outlined variant styles
              '& fieldset': { // Target the outline/border
                borderColor: 'rgba(255, 255, 255, 0.23)', // Example border color
              },
              '&:hover fieldset': {
                borderColor: 'rgba(255, 255, 255, 0.46)', // Example hover color
              },
              '&.Mui-focused fieldset': { // Focused state
                borderColor: 'rgba(255, 255, 255, 0.69)', // Adjust color
              },


            },
            // You can also set label color here if needed:
            '& .MuiInputLabel-outlined': {
              color: 'rgba(255, 255, 255, 0.54)', // Or 'white', or any color
            },
            input: { color: 'white' } // Important
          }}

        />
      </Box>

      <Box className="modal-actions">
        <Button onClick={onClose}>Cancel</Button>
        <Button
          variant="contained"
          onClick={onAdd}
          disabled={uploadedFiles.length === 0 && !importUrl}
        >
          Add
        </Button>
      </Box>
    </Box>
  );
};

export default UploadModal; 