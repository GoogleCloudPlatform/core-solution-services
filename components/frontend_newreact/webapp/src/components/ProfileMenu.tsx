import { Avatar, Menu, Box, IconButton, ListItemButton, ListItemIcon, ListItemText } from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../src/contexts/AuthContext';
import { getAuth } from "firebase/auth";

interface ProfileMenuProps {

}

export function ProfileMenu({ }: ProfileMenuProps) {
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const open = Boolean(anchorEl);
    const navigate = useNavigate();
    const { user } = useAuth(); // Get user and signOut from context
    const auth = getAuth();
    const avatarRef = useRef<HTMLButtonElement>(null);
    const logoutRef = useRef<HTMLDivElement>(null);




    useEffect(() => {
        console.log(user)
    }, [user])

    const displayName = user?.displayName || 'User';
    const userEmail = user?.email || 'user@example.com';
    const userPhotoURL = user?.photoURL; // Get photoURL
    const initials = displayName
        .split(' ')
        .map(n => n[0])
        .join('')
        .toUpperCase();


    const handleClick = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const handleLogout = async () => {  // Use async/await
        try {
            // Call the signOut function from your context (NOT auth.signOut directly)
            await auth.signOut();
            // Redirect after successful logout
            navigate('/signin');
        } catch (error) {
            // Optionally, show an error message to the user
            console.error("Logout error:", error);
        }
        handleClose();
    }

    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Tab' && avatarRef.current && avatarRef.current === document.activeElement) {
                avatarRef.current.style.boxShadow = '0 0 0 2px #4a90e2';
                avatarRef.current.style.border = '1px solid #4a90e2';
            } else if (avatarRef.current) {
                avatarRef.current.style.boxShadow = '';
                avatarRef.current.style.border = '';
            }
        };

        document.addEventListener('keydown', handleKeyDown);

        return () => {
            document.removeEventListener('keydown', handleKeyDown);
        };
    }, []);


    return (
        <Box>
            <IconButton
                onClick={handleClick}
                size="small"
                aria-controls={open ? 'account-menu' : undefined}
                aria-haspopup="true"
                aria-expanded={open ? 'true' : undefined}
                tabIndex={0}
                ref={avatarRef}
                sx={{
                    '&:focus-visible': {
                        boxShadow: '0 0 0 2px #4a90e2', /* Add focus-visible styles */
                        border: '1px solid #4a90e2',
                    },
                }}
            >
                <Avatar
                    onClick={handleClick}
                    src={userPhotoURL || undefined}
                    sx={{
                        width: 32,
                        height: 32,
                        cursor: 'pointer',
                        bgcolor: 'rgba(0, 0, 0, 0.2)',
                        color: 'white',
                        fontSize: '0.875rem'
                    }}
                >
                    {initials}
                </Avatar>
            </IconButton>
            <Menu
                anchorEl={anchorEl}
                open={open}
                onClose={handleClose}
                tabIndex={0}
                onClick={handleClose}
                PaperProps={{
                    sx: {
                        width: 200,
                        backgroundColor: '#2A2A2A',
                        border: '1px solid #3A3A3A',
                        marginTop: 1,
                        '& .MuiMenuItem-root': {
                            fontSize: '0.875rem',
                            color: 'rgba(255, 255, 255, 0.9)',
                            '&:hover': {
                                backgroundColor: 'rgba(255, 255, 255, 0.06)',
                            },
                        },
                    },
                }}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
                <Box sx={{ padding: '8px 16px' }}>
                    <Box sx={{
                        fontSize: '0.875rem',
                        fontWeight: 500,
                        color: 'white',
                    }}>
                        {displayName}
                    </Box>
                    <Box sx={{
                        fontSize: '0.75rem',
                        color: 'rgba(255, 255, 255, 0.7)',
                    }}>
                        {userEmail}
                    </Box>
                </Box>
                <ListItemButton
                    onClick={handleLogout}
                    ref={logoutRef}
                    sx={{
                        display: "flex",
                        gap: 1,
                        mt: 1,
                        padding: "8px 16px",
                        "&:focus-visible": {
                            boxShadow: "0 0 0 2px #4a90e2",
                            border: "1px solid #4a90e2",
                            borderRadius: "4px",
                        },
                    }}
                    autoFocus

                >
                    <ListItemIcon sx={{ minWidth: 0, mr: 1 }}>
                        <LogoutIcon sx={{ fontSize: 16, color: "rgba(255, 255, 255, 0.9)" }} />
                    </ListItemIcon>
                    <ListItemText
                        primary="Log Out"
                        primaryTypographyProps={{
                            sx: {
                                fontSize: "0.875rem",
                                color: "rgba(255, 255, 255, 0.9)",
                            },
                        }}
                    />
                </ListItemButton>
            </Menu>
        </Box>
    );
}
