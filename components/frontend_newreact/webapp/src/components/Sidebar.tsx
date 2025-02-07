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
import TuneIcon from '@mui/icons-material/Tune';
import ChatIcon from '@mui/icons-material/Chat';
import StorageIcon from '@mui/icons-material/Storage';
import CloudIcon from '@mui/icons-material/Cloud';
// import { ModelSelector } from "@/components/settings/model-selector";
import Divider from '@mui/material/Divider';
import ChatHistory from './ChatHistory';
import ChatScreen from './ChatScreen';
import { useSidebarStore } from '@/lib/sidebarStore';
import { Chat } from '../lib/types'; // Make sure you import the Chat type
import SettingsDrawer from './SettingsDrawer';

const drawerWidth = 60;
const collapsedWidth = 60;

interface SidebarProps {
    setShowChat: React.Dispatch<React.SetStateAction<boolean>>;
    onSelectChat: (chat: Chat) => void;
    selectedChatId?: string;
    setShowSources?: React.Dispatch<React.SetStateAction<boolean>>;
    setShowWelcome: React.Dispatch<React.SetStateAction<boolean>>;
}

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
    width: drawerWidth,
    flexShrink: 0,
    whiteSpace: 'nowrap',
    boxSizing: 'border-box',
    '& .MuiDrawer-paper': {
        width: drawerWidth,
        boxSizing: 'border-box',
        backgroundColor: '#1f1f1f',
        borderRight: '1px solid #2f2f2f',
        color: 'rgba(255, 255, 255, 0.9)',
        overflowX: 'hidden',
    },
}));

const SidePanel = styled(Box, {
    shouldForwardProp: (prop) => prop !== "isOpen" && prop !== "drawerIsOpen",
})<{ isOpen: boolean, drawerIsOpen: boolean }>(({ theme, isOpen, drawerIsOpen }) => ({
    position: 'fixed',
    left: drawerWidth,
    top: 0,
    height: '100vh',
    width: 300,
    backgroundColor: '#1f1f1f',
    borderRight: '1px solid #2f2f2f',
    transition: theme.transitions.create(['transform'], {
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

export const Sidebar: React.FC<SidebarProps> = ({ 
    setShowChat, 
    onSelectChat, 
    selectedChatId,
    setShowSources,
    setShowWelcome 
}) => {
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
        { icon: <HistoryIcon />, id: 'history' },
        { icon: <TuneIcon />, id: 'settings' },
    ];

    const bottomMenuItems = [
        { 
            icon: <ChatIcon />, 
            id: 'chat',
            onClick: () => {
                setShowChat(true);
                setShowWelcome(false);
                setShowSources?.(false);
            }
        },
        { 
            icon: <StorageIcon />, 
            id: 'sources',
            onClick: () => {
                setShowSources?.(true);
                setShowChat(false);
                setShowWelcome(false);
            }
        },
        { icon: <CloudIcon />, id: 'cloud' },
    ];

    const renderMenuItem = (item: typeof mainMenuItems[0] | typeof bottomMenuItems[0], index: number) => (
        <ListItem key={item.id} disablePadding sx={{ display: 'block' }}>
            <ListItemButton
                selected={selectedItem === item.id}
                onClick={() => {
                    if ('onClick' in item && item.onClick) {
                        item.onClick();
                    } else {
                        handleItemClick(item.id);
                    }
                }}
                sx={{
                    minHeight: 48,
                    justifyContent: 'center',
                    px: 2.5,
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
                        justifyContent: 'center',
                        color: 'rgba(255, 255, 255, 0.7)',
                    }}
                >
                    {item.icon}
                </ListItemIcon>
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
                        onClick={() => {
                            setShowChat(true);
                            setShowWelcome(false);
                        }}
                        sx={{
                            bgcolor: '#000',
                            borderRadius: '50%',
                            width: 36,
                            height: 36,
                            '&:hover': {
                                bgcolor: 'rgba(0, 0, 0, 0.9)',
                            },
                        }}
                    >
                        <AddIcon sx={{ color: 'white', fontSize: 20 }} />
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
                <Box sx={{ 
                    height: 'calc(100% - 56px)', // Subtract header height
                    overflow: 'auto'
                }}>
                    <SettingsDrawer 
                        open={activePanel === 'settings'} 
                        onClose={() => {
                            setActivePanel(null);
                            setSelectedItem(null);
                        }} 
                    />
                </Box>
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
                {/* Render ChatHistory here, inside the SidePanel */}
                {activePanel === 'history' && ( // Conditionally render
                    <ChatHistory
                        onClose={() => setActivePanel(null)} // Close panel when ChatHistory closes
                        onSelectChat={onSelectChat}  // Pass the prop
                        selectedChatId={selectedChatId}
                        isOpen={activePanel === 'history'}
                    />
                )}
            </SidePanel>
        </Box>
    );
}