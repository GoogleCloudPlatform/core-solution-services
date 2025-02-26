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
// import { ModelSelector } from "@/components/settings/model-selector";
import Divider from '@mui/material/Divider';
import ChatHistory from './ChatHistory';
import ChatScreen from './ChatScreen';
import { useSidebarStore } from '@/lib/sidebarStore';
import { Chat } from '../lib/types';
import SettingsDrawer from './SettingsDrawer';
import CloudIcon from '../assets/cloud.svg'; // Import your SVG
import ChatInterfaceIcon from '../assets/chat-icon.svg'; // Import your SVG
import SourceIcon from '../assets/source-icon.svg'; // Import your SVG
import HistoryCustomIcon from '../assets/history-icon.svg';
import SettingsCustomIcon from '../assets/settings-icon.svg';
import Tooltip from '@mui/material/Tooltip';


const drawerWidth = 150;
const collapsedWidth = 60;

interface SidebarProps {
    setShowChat: (show: boolean) => void;
    onSelectChat: (chat: Chat) => void;
    selectedChatId?: string;
    setShowSources: (show: boolean) => void;
    setShowWelcome: (show: boolean) => void;
    onNewChat: () => void;
    currentChat: Chat | undefined;
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

export const Sidebar = ({
    setShowChat,
    onSelectChat,
    selectedChatId,
    setShowSources,
    setShowWelcome,
    onNewChat,
    currentChat
}: SidebarProps) => {
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

    const handleNewChatClick = () => {
        //onNewChat();
        setShowChat(true);
        setShowWelcome(false);
        // clear the current chat for proper loading
        onSelectChat({
            id: undefined,  // undefined for new chat
            title: 'New Chat',
            created_time: new Date().toISOString(),
            created_by: '',
            last_modified_time: new Date().toISOString(),
            last_modified_by: '',
            archived_at_timestamp: null,
            archived_by: '',
            deleted_at_timestamp: null,
            deleted_by: '',
            prompt: '',
            llm_type: '',
            user_id: '',
            agent_name: null,
            history: []
        });
        console.log('click')
    }

    const mainMenuItems = [
        {
            text: 'History',
            tooltip: 'History',
            icon: <img src={HistoryCustomIcon} className="" style={{ width: '14px', height: '14px' }} alt= "History icon" />,
            id: 'history'
        },
        {
            text: 'Settings',
            tooltip: 'Settings',
            icon: <img src={SettingsCustomIcon} style={{ width: '14px', height: '14px' }} alt= "Settings icon"/>,
            id: 'settings'
        },
    ];

    const bottomMenuItems = [
        {
            text: 'Resume Chat',
            tooltip: 'Resume Chat',
            icon: <img src={ChatInterfaceIcon} style={{ width: '14px', height: '14px' }} alt="Resume Chat icon"/>,
            id: 'chat',
            onClick: () => {
                setShowChat(true);
                setShowWelcome(false);
                setShowSources?.(false);
            }
        },
        {
            text: 'Sources',
            tooltip: 'Sources',
            icon: <img src={SourceIcon} style={{ width: '14px', height: '14px' }} alt="Source icon" />,
            id: 'sources',
            onClick: () => {
                setShowSources?.(true);
                setShowChat(false);
                setShowWelcome(false);
            }
        },
        {
            icon: <img src={CloudIcon} style={{ width: '14px', height: '14px' }} alt="Google cloud icon" />,
            id: 'cloud'
        },
    ];

    const renderMenuItem = (item: typeof mainMenuItems[0] | typeof bottomMenuItems[0], index: number) => (
        <Tooltip
            title={item.tooltip}
            placement="right"
            arrow
        >
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
                        justifyContent: isOpen ? 'initial' : 'center',
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
        </Tooltip>
    );

    return (
        <Box sx={{ display: 'flex' }}>
            <StyledDrawer
                variant="permanent"
                isOpen={isOpen}
            >
                <DrawerHeader>
                    < Tooltip
                        title={isOpen ? "Collapse Sidebar" : "Expand Sidebar"}
                        placement='right'
                        arrow
                    >
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
                    </Tooltip>
                    < Tooltip
                        title='New Chat'
                        placement='right'
                        arrow
                    >
                        <IconButton
                            onClick={() => {
                                handleNewChatClick();
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
                    </Tooltip>
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
                {activePanel === 'history' && (
                    <ChatHistory
                        onClose={() => setActivePanel(null)}
                        onSelectChat={onSelectChat}
                        selectedChatId={selectedChatId}
                        isOpen={activePanel === 'history'}
                    />
                )}
            </SidePanel>
        </Box>
    );
}