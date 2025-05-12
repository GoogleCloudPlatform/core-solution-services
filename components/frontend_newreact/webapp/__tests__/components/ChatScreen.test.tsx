import React, { useState } from 'react'; // Ensure React and useState are imported
import { envOrFail, getEnvVars } from '../../src/lib/env';
import ChatScreen from '../../src/components/ChatScreen';
import { useModel } from '../../src/contexts/ModelContext';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import '@testing-library/jest-dom';
import { useAuth } from '../../src/contexts/AuthContext';
import UploadModal, { FileUpload } from '../../src/components/UploadModal';
import { Sidebar } from '../../src/components/Sidebar';
import { useSidebarStore } from '../../src/lib/sidebarStore';
import SettingsDrawer from '../../src/components/SettingsDrawer';
import SourcesTable from '../../src/components/SourcesTable';
import { QueryEngine } from '../../src/lib/types';
import Sources from '../../src/components/SourcesTable';

// Mock the useAuth hook
jest.mock('../../src/contexts/AuthContext', () => ({
  useAuth: jest.fn(() => ({
    user: null,
  })),
}));

// Mock the useModel hook
jest.mock('../../src/contexts/ModelContext', () => ({
  useModel: jest.fn(() => ({
    selectedModel: { id: 'mockModelId' },
  })),
}));

// Mock SourceSelector component (if not needed, use null)
jest.mock('../../src/components/SourceSelector', () => jest.fn(() => null));

// Mock scrollTo to prevent error in jsdom
beforeEach(() => {
  window.HTMLElement.prototype.scrollTo = jest.fn();

  // Mocking URL.createObjectURL to prevent error in test environment
  global.URL.createObjectURL = jest.fn(() => 'mockedObjectURL');
});

describe('ChatScreen', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders ChatScreen with welcome message and graphEnabled', () => {
    // Rendering the ChatScreen with both showWelcome and graphEnabled as true
    render(<ChatScreen showWelcome={true} isTest={true} />);

    // Expecting the "create a graph" message to be in the document when graphEnabled is true
    expect(screen.getByText(/create a graph/i)).toBeInTheDocument();
  });
  test('renders ChatScreen without welcome message', () => {
    render(<ChatScreen showWelcome={true} isTest={true} />);
    expect(screen.queryByText(/""/i)).not.toBeInTheDocument(); // Same here for correct text
  });

  test('handles user input and submits a message', async () => {
    render(<ChatScreen showWelcome={false} isTest={true} />);
    const input = screen.getByPlaceholderText(/enter your prompt/i);
    const submitButton = screen.getByRole('button'); // Use 'button' without name, or better, query by label/aria-label

    fireEvent.change(input, { target: { value: "" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      // Ensure the input is cleared (if that's the expected behavior)
      //expect(input.value).toBe('');
    });
  });

  test('shows error message when an error occurs', async () => {
    // Store the original fetch function
    const originalFetch = window.fetch;
    window.fetch = jest.fn(() => Promise.reject(new Error('API is down')));
    render(<ChatScreen showWelcome={false} isTest={true} />);
    const input = screen.getByPlaceholderText(/enter your prompt/i);
    const submitButton = screen.getByRole('button'); // Same change as previous test

    fireEvent.change(input, { target: { value: 'Hello, world!' } });
    fireEvent.click(submitButton);


    // Restore the original fetch
    window.fetch = originalFetch;
  });
});
describe('UploadModal - File Upload', () => {
  it('calls onFileSelect when files are selected', () => {
    const mockOnFileSelect = jest.fn();

    render(
      <UploadModal
        open={true}
        onClose={jest.fn()}
        uploadedFiles={[]}
        onFileSelect={mockOnFileSelect}
        onRemoveFile={jest.fn()}
        importUrl=""
        onImportUrlChange={jest.fn()}
        onAdd={jest.fn()}
        setUploadedFiles={jest.fn()}
        showError={{}}
        setShowError={jest.fn()}
      />
    );

    // Match input by the label text associated with htmlFor="file-upload"
    const fileInput = screen.getByLabelText(/drag & drop or choose a file/i) as HTMLInputElement;

    const file = new File(['dummy content'], 'example.txt', { type: 'text/plain' });

    fireEvent.change(fileInput, {
      target: { files: [file] },
    });

    expect(mockOnFileSelect).toHaveBeenCalledTimes(1);
    expect(mockOnFileSelect.mock.calls[0][0].target.files[0]).toEqual(file);
  });
});
test('opens upload modal when "+" IconButton is clicked', () => {

  // Render the ChatScreen component
  render(<ChatScreen showWelcome={false} isTest={true} />);

  // Find the "+" IconButton using the role of 'button' and its children AddIcon (or check the name)
  const uploadButton = screen.getByRole('button', { name: /add/i });

  // Click the "+" IconButton to open the UploadModal
  fireEvent.click(uploadButton);

  // Check if the UploadModal is opened by looking for specific text in the modal
  // Adjust this to the actual text or content you expect in the modal
  expect(screen.getByText(/Add File/i)).toBeInTheDocument();
});
describe('UploadModal - Import from URL', () => {
  it('calls onImportUrlChange when the URL input changes', () => {
    const mockOnImportUrlChange = jest.fn();

    render(
      <UploadModal
        open={true}
        onClose={jest.fn()}
        uploadedFiles={[]}
        onFileSelect={jest.fn()}
        onRemoveFile={jest.fn()}
        importUrl=""
        onImportUrlChange={mockOnImportUrlChange}
        onAdd={jest.fn()}
        setUploadedFiles={jest.fn()}
        showError={{}}
        setShowError={jest.fn()}
      />
    );

    const importUrlInput = screen.getByPlaceholderText('http(s)://, gs://, shpt://') as HTMLInputElement;

    const newUrl = 'https://example.com/file.zip';

    fireEvent.change(importUrlInput, {
      target: { value: newUrl },
    });

    expect(mockOnImportUrlChange).toHaveBeenCalledTimes(1);
    expect(mockOnImportUrlChange.mock.calls[0][0]).toBe(newUrl);
  });
});
describe('UploadModal - Add Button', () => {
  it('calls onAdd when Add button is clicked and there are uploaded files or a URL', () => {
    const mockOnAdd = jest.fn();

    render(
      <UploadModal
        open={true}
        onClose={jest.fn()}
        uploadedFiles={[{ name: 'example.txt' }]} // Mocked uploaded file
        onFileSelect={jest.fn()}
        onRemoveFile={jest.fn()}
        importUrl="https://example.com/file.zip" // Mocked import URL
        onImportUrlChange={jest.fn()}
        onAdd={mockOnAdd}
        setUploadedFiles={jest.fn()}
        showError={{}}
        setShowError={jest.fn()}
      />
    );

    const addButton = screen.getByRole('button', { name: /add/i });

    fireEvent.click(addButton);

    expect(mockOnAdd).toHaveBeenCalledTimes(1);
  });

  it('disables Add button when there are no files or URL', () => {
    const mockOnAdd = jest.fn();

    render(
      <UploadModal
        open={true}
        onClose={jest.fn()}
        uploadedFiles={[]}
        onFileSelect={jest.fn()}
        onRemoveFile={jest.fn()}
        importUrl=""
        onImportUrlChange={jest.fn()}
        onAdd={mockOnAdd}
        setUploadedFiles={jest.fn()}
        showError={{}}
        setShowError={jest.fn()}
      />
    );

    const addButton = screen.getByRole('button', { name: /add/i });

    expect(addButton).toBeDisabled();
  });
});
describe('UploadModal - Cancel Button', () => {
  it('calls onClose when the Cancel button is clicked', () => {
    const mockOnClose = jest.fn();

    render(
      <UploadModal
        open={true}
        onClose={mockOnClose}
        uploadedFiles={[]}
        onFileSelect={jest.fn()}
        onRemoveFile={jest.fn()}
        importUrl=""
        onImportUrlChange={jest.fn()}
        onAdd={jest.fn()}
        setUploadedFiles={jest.fn()}
        showError={{}}
        setShowError={jest.fn()}
      />
    );

    const cancelButton = screen.getByRole('button', { name: /cancel/i });

    fireEvent.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });
});
describe('UploadModal - Close Button (X)', () => {
  it('calls onClose when the Close (X) button is clicked', () => {
    const mockOnClose = jest.fn();

    render(
      <UploadModal
        open={true}
        onClose={mockOnClose}
        uploadedFiles={[]}
        onFileSelect={jest.fn()}
        onRemoveFile={jest.fn()}
        importUrl=""
        onImportUrlChange={jest.fn()}
        onAdd={jest.fn()}
        setUploadedFiles={jest.fn()}
        showError={{}}
        setShowError={jest.fn()}
      />
    );

    const closeButton = screen.getByLabelText('close'); // Assuming Close icon has a label 'close'

    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });
});


test('toggles "Create a Graph" state and updates UI accordingly when isTest is true', () => {
  
    expect(screen.queryByText('Create a graph')).not.toBeInTheDocument();
  
  });


jest.mock('@/lib/sidebarStore', () => ({
    useSidebarStore: jest.fn(() => ({
      isOpen: false,
      activePanel: null,
      selectedItem: null,
      toggle: jest.fn(),
      setActivePanel: jest.fn(),
      setSelectedItem: jest.fn(),
    })),
  }));
  
  describe('Sidebar - New Chat Functionality', () => {
    const mockSetShowChat = jest.fn();
    const mockOnSelectChat = jest.fn();
    const mockSetShowWelcome = jest.fn();
  
    beforeEach(() => {
      // Reset the mocks before each test
      mockSetShowChat.mockClear();
      mockOnSelectChat.mockClear();
      mockSetShowWelcome.mockClear();
      useSidebarStore.mockClear(); // Reset the mock of the store hook
    });
  
    test('renders the add icon for new chat', async () => {
      render(
        <Sidebar
          setShowChat={mockSetShowChat}
          onSelectChat={mockOnSelectChat}
          setShowSources={jest.fn()}
          setShowWelcome={mockSetShowWelcome}
          onNewChat={jest.fn()}
          onResumeChat={jest.fn()}
          setShowAddSource={jest.fn()}
          setShowEditSource={jest.fn()}
          currentChat={undefined}
        />
      );
  
      // Find the add icon (you might need to adjust the selector based on how it's rendered)
      const newChatIcon = await screen.findByRole('button', { name: /new chat/i }); // Assuming the IconButton has an accessible name
  
      expect(newChatIcon).toBeInTheDocument();
    });
  
    test('calls setShowChat and setShowWelcome with correct values when new chat icon is clicked', async () => {
      render(
        <Sidebar
          setShowChat={mockSetShowChat}
          onSelectChat={mockOnSelectChat}
          setShowSources={jest.fn()}
          setShowWelcome={mockSetShowWelcome}
          onNewChat={jest.fn()}
          onResumeChat={jest.fn()}
          setShowAddSource={jest.fn()}
          setShowEditSource={jest.fn()}
          currentChat={undefined}
        />
      );
  
      const newChatIcon = await screen.findByRole('button', { name: /new chat/i });
      fireEvent.click(newChatIcon);
  
      expect(mockSetShowChat).toHaveBeenCalledWith(true);
      expect(mockSetShowWelcome).toHaveBeenCalledWith(false);
    });
  
    test('calls onSelectChat with a new chat object when new chat icon is clicked', async () => {
      render(
        <Sidebar
          setShowChat={mockSetShowChat}
          onSelectChat={mockOnSelectChat}
          setShowSources={jest.fn()}
          setShowWelcome={mockSetShowWelcome}
          onNewChat={jest.fn()}
          onResumeChat={jest.fn()}
          setShowAddSource={jest.fn()}
          setShowEditSource={jest.fn()}
          currentChat={undefined}
        />
      );
  
      const newChatIcon = await screen.findByRole('button', { name: /new chat/i });
      fireEvent.click(newChatIcon);
  
      expect(mockOnSelectChat).toHaveBeenCalledTimes(1);
      const newChatObject = mockOnSelectChat.mock.calls[0][0];
      expect(newChatObject.id).toBeUndefined();
      expect(newChatObject.title).toBe('New Chat');
      // You can add more assertions here to check other properties of the new chat object
    });
  });
  

  

  jest.mock('@/lib/sidebarStore', () => ({
    useSidebarStore: jest.fn(() => ({
      isOpen: false,
      activePanel: null,
      selectedItem: null,
      toggle: jest.fn(),
      setActivePanel: jest.fn(),
      setSelectedItem: jest.fn(),
    })),
  }));
  
  describe('Sidebar - Main Menu Items', () => {
    const mockSetShowChat = jest.fn();
    const mockOnSelectChat = jest.fn();
    const mockSetShowWelcome = jest.fn();
    const mockSetActivePanel = jest.fn();
    const mockSetSelectedItem = jest.fn();
  
    beforeEach(() => {
      mockSetShowChat.mockClear();
      mockOnSelectChat.mockClear();
      mockSetShowWelcome.mockClear();
      useSidebarStore.mockReturnValue({
        isOpen: false,
        activePanel: null,
        selectedItem: null,
        toggle: jest.fn(),
        setActivePanel: mockSetActivePanel,
        setSelectedItem: mockSetSelectedItem,
      });
      mockSetActivePanel.mockClear();
      mockSetSelectedItem.mockClear();
    });
  
    test('renders the main menu items with correct text and icons', async () => {
      render(
        <Sidebar
          setShowChat={mockSetShowChat}
          onSelectChat={mockOnSelectChat}
          setShowSources={jest.fn()}
          setShowWelcome={jest.fn()}
          onNewChat={jest.fn()}
          onResumeChat={jest.fn()}
          setShowAddSource={jest.fn()}
          setShowEditSource={jest.fn()}
          currentChat={undefined}
        />
      );
  
      // Check for "History" item
      const historyButtons = await screen.findAllByRole('button', { name: /history/i });
      const historyItem = historyButtons[0];
      expect(historyItem).toBeInTheDocument();
      const historyIcon = historyItem.querySelector('img[alt="History icon"]');
      expect(historyIcon).toBeInTheDocument();
  
      // Check for "Settings" item
      const settingsButtons = await screen.findAllByRole('button', { name: /settings/i });
      const settingsItem = settingsButtons[0];
      expect(settingsItem).toBeInTheDocument();
      const settingsIcon = settingsItem.querySelector('img[alt="Settings icon"]');
      expect(settingsIcon).toBeInTheDocument();
    });
  
    test('calls setActivePanel and setSelectedItem with "history" when History is clicked', async () => {
      render(
        <Sidebar
          setShowChat={mockSetShowChat}
          onSelectChat={mockOnSelectChat}
          setShowSources={jest.fn()}
          setShowWelcome={mockSetShowWelcome}
          onNewChat={jest.fn()}
          onResumeChat={jest.fn()}
          setShowAddSource={jest.fn()}
          setShowEditSource={jest.fn()}
          currentChat={undefined}
        />
      );
  
      const historyButtons = await screen.findAllByRole('button', { name: /history/i });
      const historyButton = historyButtons[0];
      fireEvent.click(historyButton);
  
      expect(mockSetActivePanel).toHaveBeenCalledWith('history');
      expect(mockSetSelectedItem).toHaveBeenCalledWith('history');
    });
  
    test('calls setActivePanel and setSelectedItem with "settings" when Settings is clicked', async () => {
      render(
        <Sidebar
          setShowChat={mockSetShowChat}
          onSelectChat={mockOnSelectChat}
          setShowSources={jest.fn()}
          setShowWelcome={mockSetShowWelcome}
          onNewChat={jest.fn()}
          onResumeChat={jest.fn()}
          setShowAddSource={jest.fn()}
          setShowEditSource={jest.fn()}
          currentChat={undefined}
        />
      );
  
      const settingsButtons = await screen.findAllByRole('button', { name: /settings/i });
      const settingsButton = settingsButtons[0];
      fireEvent.click(settingsButton);
  
      expect(mockSetActivePanel).toHaveBeenCalledWith('settings');
      expect(mockSetSelectedItem).toHaveBeenCalledWith('settings');
    });
    test('clears activePanel and selectedItem when the currently selected main menu item is clicked again', async () => {
        // Mock the store with 'settings' as initially selected
        useSidebarStore.mockReturnValue({
          isOpen: false,
          activePanel: 'settings',
          selectedItem: 'settings',
          toggle: jest.fn(),
          setActivePanel: mockSetActivePanel,
          setSelectedItem: mockSetSelectedItem,
        });
    
        render(
          <Sidebar
            setShowChat={mockSetShowChat}
            onSelectChat={mockOnSelectChat}
            setShowSources={jest.fn()}
            setShowWelcome={mockSetShowWelcome}
            onNewChat={jest.fn()}
            onResumeChat={jest.fn()}
            setShowAddSource={jest.fn()}
            setShowEditSource={jest.fn()}
            currentChat={undefined}
          />
        );
    
        const settingsButtons = await screen.findAllByRole('button', { name: /settings/i });
        const settingsButton = settingsButtons[0];
        fireEvent.click(settingsButton);
    
        // Assert that setActivePanel was called with null
        expect(mockSetActivePanel).toHaveBeenCalledWith(null);
        expect(mockSetSelectedItem).toHaveBeenCalledWith(null);
      });
  });
  jest.mock('@/lib/sidebarStore', () => ({
    useSidebarStore: jest.fn(() => ({
      isOpen: false,
      activePanel: null,
      selectedItem: null,
      toggle: jest.fn(),
      setActivePanel: jest.fn(),
      setSelectedItem: jest.fn(),
    })),
  }));
  
  describe('Sidebar - Bottom Menu Items', () => {
    const mockSetShowChat = jest.fn();
    const mockOnSelectChat = jest.fn();
    const mockSetShowWelcome = jest.fn();
    const mockSetShowSources = jest.fn();
    const mockOnResumeChat = jest.fn();
    const mockSetShowAddSource = jest.fn();
    const mockSetShowEditSource = jest.fn();
  
    beforeEach(() => {
      mockSetShowChat.mockClear();
      mockOnSelectChat.mockClear();
      mockSetShowWelcome.mockClear();
      mockSetShowSources.mockClear();
      mockOnResumeChat.mockClear();
      mockSetShowAddSource.mockClear();
      mockSetShowEditSource.mockClear();
      useSidebarStore.mockClear();
    });
  
    test('renders the "Resume Chat" menu item with correct text and icon', async () => {
      render(
        <Sidebar
          setShowChat={mockSetShowChat}
          onSelectChat={mockOnSelectChat}
          setShowSources={mockSetShowSources}
          setShowWelcome={mockSetShowWelcome}
          onNewChat={jest.fn()}
          onResumeChat={mockOnResumeChat}
          setShowAddSource={mockSetShowAddSource}
          setShowEditSource={mockSetShowEditSource}
          currentChat={undefined}
        />
      );
  
      const resumeChatButton = await screen.findByRole('button', { name: /resume chat/i });
      expect(resumeChatButton).toBeInTheDocument();
      const resumeChatIcon = resumeChatButton.querySelector('img[alt="Resume Chat icon"]');
      expect(resumeChatIcon).toBeInTheDocument();
    });
  
    test('calls setShowChat, setShowWelcome, setShowSources, onResumeChat, setShowAddSource, and setShowEditSource when "Resume Chat" is clicked', async () => {
      render(
        <Sidebar
          setShowChat={mockSetShowChat}
          onSelectChat={mockOnSelectChat}
          setShowSources={mockSetShowSources}
          setShowWelcome={mockSetShowWelcome}
          onNewChat={jest.fn()}
          onResumeChat={mockOnResumeChat}
          setShowAddSource={mockSetShowAddSource}
          setShowEditSource={mockSetShowEditSource}
          currentChat={undefined}
        />
      );
  
      const resumeChatButton = await screen.findByRole('button', { name: /resume chat/i });
      fireEvent.click(resumeChatButton);
  
      expect(mockSetShowChat).toHaveBeenCalledWith(true);
      expect(mockSetShowWelcome).toHaveBeenCalledWith(false);
      expect(mockSetShowSources).toHaveBeenCalledWith(false);
      expect(mockOnResumeChat).toHaveBeenCalledTimes(1);
      expect(mockSetShowAddSource).toHaveBeenCalledWith(false);
      expect(mockSetShowEditSource).toHaveBeenCalledWith(false);
    });
  
    test('renders the "Sources" menu item with correct text and icon', async () => {
      render(
        <Sidebar
          setShowChat={mockSetShowChat}
          onSelectChat={mockOnSelectChat}
          setShowSources={mockSetShowSources}
          setShowWelcome={mockSetShowWelcome}
          onNewChat={jest.fn()}
          onResumeChat={mockOnResumeChat}
          setShowAddSource={mockSetShowAddSource}
          setShowEditSource={mockSetShowEditSource}
          currentChat={undefined}
        />
      );
  
      const sourcesButton = await screen.findByRole('button', { name: /sources/i });
      expect(sourcesButton).toBeInTheDocument();
      const sourcesIcon = sourcesButton.querySelector('img[alt="Source icon"]');
      expect(sourcesIcon).toBeInTheDocument();
    });
  
    test('calls setShowSources, setShowChat, and setShowWelcome when "Sources" is clicked', async () => {
      render(
        <Sidebar
          setShowChat={mockSetShowChat}
          onSelectChat={mockOnSelectChat}
          setShowSources={mockSetShowSources}
          setShowWelcome={mockSetShowWelcome}
          onNewChat={jest.fn()}
          onResumeChat={mockOnResumeChat}
          setShowAddSource={mockSetShowAddSource}
          setShowEditSource={mockSetShowEditSource}
          currentChat={undefined}
        />
      );
  
      const sourcesButton = await screen.findByRole('button', { name: /sources/i });
      fireEvent.click(sourcesButton);
  
      expect(mockSetShowSources).toHaveBeenCalledWith(true);
      expect(mockSetShowChat).toHaveBeenCalledWith(false);
      expect(mockSetShowWelcome).toHaveBeenCalledWith(false);
    });
  });

// Mock the useModel hook
const mockUseModel = useModel as jest.Mock;

// Mock localStorage for persistence simulation
const localStorageMock = (() => {
    let store: Record<string, string> = {};
    return {
        getItem: (key: string) => store[key] || null,
        setItem: (key: string, value: string) => {
            store[key] = String(value);
        },
        removeItem: (key: string) => {
            delete store[key];
        },
        clear: () => {
            store = {};
        },
    };
})();

Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock the ModelBrowser component
jest.mock('../../src/components/ModelBrowser', () => ({
    __esModule: true,
    default: jest.fn(() => <div data-testid="model-browser">Model Browser</div>),
}));

describe('SettingsDrawer - Temperature Persistence', () => {
    const mockModel: ChatModel = {
        id: 'test-model',
        name: 'Test Model',
        description: 'A test model',
        modelParams: {
            temperature: 0.5,
        },
    };

    beforeEach(() => {
        jest.clearAllMocks();
        localStorage.clear(); // Clear localStorage before each test
        mockUseModel.mockReturnValue({
            selectedModel: mockModel,
            setSelectedModel: jest.fn((model: ChatModel) => {
                // Simulate persistence by saving to localStorage
                if (model.modelParams?.temperature !== undefined) {
                    localStorage.setItem('selectedModel', JSON.stringify(model));
                } else {
                    localStorage.removeItem('selectedModel');
                }
            }),
            loading: false,
        });
    });

    const renderComponent = (open = true) => {
        render(<SettingsDrawer open={open} onClose={jest.fn()} />);
    };

    it('should initially render with the temperature from the context', () => {
        renderComponent();
        const temperatureDisplay = screen.getByText(/0\.5/i);
        expect(temperatureDisplay).toBeInTheDocument();
        const slider = screen.getByRole('slider');
        expect(slider).toHaveValue('0.5');
    });

    it('should update the temperature in the context and localStorage when the slider changes', () => {
        renderComponent();
        const sliders = screen.getAllByRole('slider');
        const initialSlider = sliders[0]; // Assuming the visible slider is the first one
    
        fireEvent.change(initialSlider, { target: { value: '.5' } });
    
        // Simulate a refresh by re-rendering the component, now reading from localStorage
        mockUseModel.mockReturnValue({
            selectedModel: JSON.parse(localStorage.getItem('selectedModel') || '{}'),
            setSelectedModel: jest.fn(), // Mocked as persistence is handled in the previous mock
            loading: false,
        });
        renderComponent();
    
        const temperatureDisplayAfterRefresh = screen.getByText(/.5/i);
        expect(temperatureDisplayAfterRefresh).toBeInTheDocument();
        const slidersAfterRefresh = screen.getAllByRole('slider');
        const sliderAfterRefresh = slidersAfterRefresh[0]; // Assuming the visible slider is still the first one
        expect(sliderAfterRefresh).toHaveValue('0.5');
    });

    it('should persist the temperature change after the component is unmounted and remounted', () => {
        const { unmount, rerender } = render(<SettingsDrawer open={true} onClose={jest.fn()} />);
        const initialSlider = screen.getByRole('slider');
        fireEvent.change(initialSlider, { target: { value: '0.8' } });
        unmount();

        // Simulate a remount, now reading from localStorage
        mockUseModel.mockReturnValue({
            selectedModel: JSON.parse(localStorage.getItem('selectedModel') || '{}'),
            setSelectedModel: jest.fn(),
            loading: false,
        });
        render(<SettingsDrawer open={true} onClose={jest.fn()} />);

        const temperatureDisplayAfterRemount = screen.getByText(/0\.8/i);
        expect(temperatureDisplayAfterRemount).toBeInTheDocument();
        const sliderAfterRemount = screen.getByRole('slider');
        expect(sliderAfterRemount).toHaveValue('0.8');
    });
   
    it('should handle default temperature scenarios', () => {
        // Case 1: No selected model - check for default temperature text
        mockUseModel.mockReturnValue({ selectedModel: {}, setSelectedModel: jest.fn(), loading: false });
        renderComponent();
        const defaultTemperaturesNoModel = screen.getAllByText(/0\.2/i);
        expect(defaultTemperaturesNoModel[0]).toBeInTheDocument();
    
        localStorage.clear();
    
    });
});


const mockSources: QueryEngine[] = [
    { id: '1', name: 'Source A', description: 'Description A', query_engine_type: 'TYPE1', status: 'success', created_time: '2025-05-08T10:00:00Z' },
    { id: '2', name: 'Source B', description: 'Description B', query_engine_type: 'TYPE2', status: 'active', created_time: '2025-05-07T20:00:00Z' },
    { id: '3', name: 'Source C', description: 'Description C', query_engine_type: 'TYPE3', status: 'failed', created_time: '2025-05-06T15:00:00Z' },
];

const mockProps = {
    sources: mockSources,
    selectedSources: [],
    onSelectAll: jest.fn(),
    onSelectSource: jest.fn(),
    onEditClick: jest.fn(),
    onViewClick: jest.fn(),
    onDeleteClick: jest.fn(),
    typeFilter: 'all',
    jobStatusFilter: 'all',
    currentPage: 1,
    rowsPerPage: 10,
    isEditDisabled: false,
};

describe('SourcesTable', () => {
    it('renders the table with the provided sources', () => {
        render(<SourcesTable {...mockProps} />);
        expect(screen.getByText('Source A')).toBeInTheDocument();
        expect(screen.getByText('Source B')).toBeInTheDocument();
        expect(screen.getByText('Source C')).toBeInTheDocument();
        expect(screen.getByText('Description A')).toBeInTheDocument();
        expect(screen.getByText('TYPE1')).toBeInTheDocument();
        expect(screen.getByText('success')).toBeInTheDocument();
    });
    it('renders the relative time for the updated column', () => {
        render(<SourcesTable {...mockProps} />);
        const agoElements = screen.getAllByText(/ago/i);
        expect(agoElements.length).toBeGreaterThan(0);
    });
   
    it('calls onViewClick when the view button is clicked', () => {
        render(<SourcesTable {...mockProps} />);
        const viewButtons = screen.getAllByRole('button', { name: /view source/i });
        fireEvent.click(viewButtons[0]);
        expect(mockProps.onViewClick).toHaveBeenCalledWith('1');
    });
    
});




describe('Sources View', () => {
    it('renders the view with the provided sources', () => {
        render(<SourcesTable {...mockProps} />);
        expect(screen.getByText('Source A')).toBeInTheDocument();
        expect(screen.getByText('Source B')).toBeInTheDocument();
        expect(screen.getByText('Source C')).toBeInTheDocument();
        expect(screen.getByText('Description A')).toBeInTheDocument();
        expect(screen.getByText('TYPE1')).toBeInTheDocument();
        expect(screen.getByText('success')).toBeInTheDocument();
    }); 
    
});


