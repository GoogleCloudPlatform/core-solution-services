import { Drawer, List, ListItem, ListItemIcon, ListItemText, Typography } from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';
import React from 'react';

interface SettingsDrawerProps {
    open: boolean;
    onClose: () => void;
}

const SettingsDrawer: React.FC<SettingsDrawerProps> = ({ open, onClose }) => {
    return (
        <Drawer anchor="left" open={open} onClose={onClose}>
            <List>
                <Typography variant="h6" sx={{ padding: 2 }}>
                    Settings
                </Typography>
                <ListItem button>
                    <ListItemIcon>
                        <SettingsIcon />
                    </ListItemIcon>
                    <ListItemText primary="Setting 1" />
                </ListItem>
                {/* Add more settings list items as needed */}
            </List>
        </Drawer>
    );
};

export default SettingsDrawer;

