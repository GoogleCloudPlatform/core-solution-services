import { Avatar, Menu, MenuItem } from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useEffect } from 'react';
import { getAuth } from "firebase/auth";

interface ProfileMenuProps {

}

export function ProfileMenu({ }: ProfileMenuProps) {
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const open = Boolean(anchorEl);
    const navigate = useNavigate();
    const { user } = useAuth(); // Get user and signOut from context
    const auth = getAuth();


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

    return (
        <>
            <Avatar
                onClick={handleClick}
                src={userPhotoURL}
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
            <Menu
                anchorEl={anchorEl}
                open={open}
                onClose={handleClose}
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
                <div style={{ padding: '8px 16px' }}>
                    <div style={{
                        fontSize: '0.875rem',
                        fontWeight: 500,
                        color: 'white',
                    }}
                    >
                        {displayName}
                    </div>
                    <div style={{
                        fontSize: '0.75rem',
                        color: 'rgba(255, 255, 255, 0.7)',
                    }}
                    >
                        {userEmail}
                    </div>
                </div>
                <MenuItem onClick={handleLogout} sx={{
                    display: 'flex',
                    gap: 1,
                    mt: 1,
                }}>
                    <LogoutIcon sx={{ fontSize: 16 }} />
                    <span>Log Out</span>
                </MenuItem>
            </Menu>
        </>
    );
}
