import { Box, styled } from "@mui/material";
import { ProfileMenu } from "@/components/profile-menu";

interface HeaderProps {
    sidebarWidth: number;
    panelWidth: number;
    title?: React.ReactNode;
    rightContent?: React.ReactNode;
}

const HeaderContainer = styled(Box, {
    shouldForwardProp: (prop) => prop !== "sidebarWidth" && prop !== "panelWidth",
})<{ sidebarWidth: number, panelWidth: number }>(({ theme, sidebarWidth, panelWidth }) => ({
    position: 'fixed',
    zIndex: 50,
    padding: theme.spacing(2),
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    background: `linear-gradient(to bottom, ${theme.palette.background.default}CC, ${theme.palette.background.default}00)`,
    right: 0,
    left: `${sidebarWidth + panelWidth}px`,
    transition: 'left 0.3s ease-in-out',
}));

const Title = styled(Box)({
    fontSize: '22px',
    fontWeight: 500,
    fontFamily: 'Google Sans',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    '& .primary': {
        color: '#E3E3E3',
    },
    '& .gradient': {
        background: 'linear-gradient(to right, #4C8DF6, #FF0000)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
    },
});

export function CustomHeader({ sidebarWidth, panelWidth, title, rightContent }: HeaderProps) {

    return (
        <HeaderContainer sidebarWidth={sidebarWidth} panelWidth={panelWidth}>
            {title || (
                <Title>
                    <span className="primary">genAI</span>
                    <span className="gradient">for Public Sector</span>
                </Title>
            )}
            {rightContent || (
                <ProfileMenu />
            )}
        </HeaderContainer>
    );
}

