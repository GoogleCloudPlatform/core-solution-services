/**
 * Sidebar Component
 * 
 * A Material UI based sidebar navigation component.
 */

import { useState } from 'react';
import { styled } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import AddIcon from '@mui/icons-material/Add';
import HistoryIcon from '@mui/icons-material/History';
import SettingsIcon from '@mui/icons-material/Settings';
import ChatIcon from '@mui/icons-material/Chat';
import StorageIcon from '@mui/icons-material/Storage';
import CloudIcon from '@mui/icons-material/Cloud';
// import { ModelSelector } from "@/components/settings/model-selector";
import Divider from '@mui/material/Divider';
import { useSidebarStore } from '@/lib/sidebarStore';

const drawerWidth = 150;
const collapsedWidth = 52;

const DrawerHeader = styled('div')(({ theme }) => ({
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: theme.spacing(1),
    gap: theme.spacing(1),
    ...theme.mixins.toolbar,
}));

const StyledDrawer = styled(Drawer, {
    shouldForwardProp: (prop) => prop !== "isOpen",
})<{ isOpen: boolean }>(({ theme, isOpen }) => ({
    width: isOpen ? drawerWidth : collapsedWidth,
    flexShrink: 0,
    whiteSpace: 'nowrap',
    boxSizing: 'border-box',
    '& .MuiDrawer-paper': {
        width: isOpen ? drawerWidth : collapsedWidth,
        boxSizing: 'border-box',
        backgroundColor: '#1f1f1f',
        borderRight: '1px solid #2f2f2f',
        color: 'rgba(255, 255, 255, 0.9)',
        overflowX: 'hidden',
        transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
        }),
    },
}));

const SidePanel = styled(Box, {
    shouldForwardProp: (prop) => prop !== "isOpen" && prop !== "drawerIsOpen",
})<{ isOpen: boolean, drawerIsOpen: boolean }>(({ theme, isOpen, drawerIsOpen }) => ({
    position: 'fixed',
    left: drawerIsOpen ? drawerWidth : collapsedWidth,
    top: 0,
    height: '100vh',
    width: 300,
    backgroundColor: '#1f1f1f',
    borderRight: '1px solid #2f2f2f',
    transition: theme.transitions.create(['left', 'transform'], {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.enteringScreen,
    }),
    transform: isOpen ? 'translateX(0)' : 'translateX(-100%)',
    zIndex: 30,
    display: 'flex',
    flexDirection: 'column',
}));

const PanelHeader = styled(Box)(({ theme }) => ({
    padding: theme.spacing(2),
    borderBottom: '1px solid #2f2f2f',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
}));

export function Sidebar() {
    const { isOpen, activePanel, selectedItem, toggle, setActivePanel, setSelectedItem } = useSidebarStore();

    const handleItemClick = (item: string) => {
        if (selectedItem === item) {
            setSelectedItem(null);
            setActivePanel(null);
        } else {
            setSelectedItem(item);
            setActivePanel(item as 'history' | 'settings');
        }
    };

    const mainMenuItems = [
        { text: 'History', icon: <HistoryIcon />, id: 'history' },
        { text: 'Settings', icon: <SettingsIcon />, id: 'settings' },
    ];

    const bottomMenuItems = [
        { text: 'Chat', icon: <ChatIcon />, id: 'chat' },
        { text: 'Sources', icon: <StorageIcon />, id: 'sources' },
        { text: 'GCP Cloud', icon: <CloudIcon />, id: 'cloud' },
    ];

    const renderMenuItem = (item: typeof mainMenuItems[0], index: number) => (
        <ListItem key={item.id} disablePadding sx={{ display: 'block' }}>
            <ListItemButton
                selected={selectedItem === item.id}
                onClick={() => handleItemClick(item.id)}
                sx={{
                    minHeight: 42,
                    px: 1.75,
                    justifyContent: isOpen ? 'initial' : 'center',
                    '&.Mui-selected': {
                        backgroundColor: 'rgba(0, 0, 0, 0.2)',
                    },
                    '&:hover': {
                        backgroundColor: 'rgba(255, 255, 255, 0.06)',
                    },
                }}
            >
                <ListItemIcon
                    sx={{
                        minWidth: 0,
                        mr: isOpen ? 2 : 'auto',
                        justifyContent: 'center',
                        color: 'rgba(255, 255, 255, 0.7)',
                    }}
                >
                    {item.icon}
                </ListItemIcon>
                <ListItemText
                    primary={item.text}
                    sx={{
                        opacity: isOpen ? 1 : 0,
                        transition: 'opacity 0.2s',
                        '& .MuiTypography-root': {
                            color: 'rgba(255, 255, 255, 0.9)',
                            fontSize: '0.875rem',
                        },
                    }}
                />
            </ListItemButton>
        </ListItem>
    );

    return (
        <Box sx={{ display: 'flex' }}>
            <StyledDrawer
                variant="permanent"
                isOpen={isOpen}
            >
                <DrawerHeader>
                    <IconButton
                        onClick={toggle}
                        sx={{
                            color: 'rgba(255, 255, 255, 0.7)',
                            '&:hover': {
                                backgroundColor: 'rgba(255, 255, 255, 0.06)',
                            },
                        }}
                    >
                        <MenuIcon />
                    </IconButton>
                    <IconButton
                        sx={{
                            bgcolor: '#000',
                            borderRadius: '50%',
                            '&:hover': {
                                bgcolor: 'rgba(0, 0, 0, 0.9)',
                            },
                        }}
                    >
                        <AddIcon sx={{ color: 'white' }} />
                    </IconButton>
                </DrawerHeader>

                <List sx={{ mt: 1 }}>
                    {mainMenuItems.map(renderMenuItem)}
                </List>

                <List sx={{ mt: 'auto', mb: 2 }}>
                    {bottomMenuItems.map(renderMenuItem)}
                </List>
            </StyledDrawer>

            {/* Settings Panel */}
            <SidePanel
                isOpen={activePanel === 'settings'}
                drawerIsOpen={isOpen}
            >
                <PanelHeader>
                    <Box sx={{ typography: 'subtitle2', color: 'rgba(255, 255, 255, 0.9)' }}>
                        Settings
                    </Box>
                    <IconButton
                        onClick={() => {
                            setActivePanel(null);
                            setSelectedItem(null);
                        }}
                        sx={{
                            color: 'rgba(255, 255, 255, 0.7)',
                            '&:hover': {
                                backgroundColor: 'rgba(255, 255, 255, 0.06)',
                            },
                        }}
                    >
                        <MenuIcon />
                    </IconButton>
                </PanelHeader>
                {/* <Box sx={{ p: 2 }}>
                    <ModelSelector />
                </Box> */}
            </SidePanel>

            {/* History Panel */}
            <SidePanel
                isOpen={activePanel === 'history'}
                drawerIsOpen={isOpen}
            >
                <PanelHeader>
                    <Box sx={{ typography: 'subtitle2', color: 'rgba(255, 255, 255, 0.9)' }}>
                        History
                    </Box>
                    <IconButton
                        onClick={() => {
                            setActivePanel(null);
                            setSelectedItem(null);
                        }}
                        sx={{
                            color: 'rgba(255, 255, 255, 0.7)',
                            '&:hover': {
                                backgroundColor: 'rgba(255, 255, 255, 0.06)',
                            },
                        }}
                    >
                        <MenuIcon />
                    </IconButton>
                </PanelHeader>
                <List>
                    <ListItem disablePadding>
                        <ListItemButton
                            sx={{
                                py: 0.5,
                                '&:hover': {
                                    backgroundColor: 'rgba(255, 255, 255, 0.06)',
                                },
                            }}
                        >
                            <ListItemText
                                primary="Topical Gist"
                                sx={{
                                    '& .MuiTypography-root': {
                                        fontSize: '0.875rem',
                                        color: 'rgba(255, 255, 255, 0.7)',
                                    },
                                }}
                            />
                        </ListItemButton>
                    </ListItem>
                    <ListItem disablePadding>
                        <ListItemButton
                            sx={{
                                py: 0.5,
                                '&:hover': {
                                    backgroundColor: 'rgba(255, 255, 255, 0.06)',
                                },
                            }}
                        >
                            <ListItemText
                                primary="Recent Chat 2"
                                sx={{
                                    '& .MuiTypography-root': {
                                        fontSize: '0.875rem',
                                        color: 'rgba(255, 255, 255, 0.7)',
                                    },
                                }}
                            />
                        </ListItemButton>
                    </ListItem>
                </List>
            </SidePanel>
        </Box>
    );
}