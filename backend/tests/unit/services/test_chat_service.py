import pytest
from unittest.mock import AsyncMock
from app.domain.chat.service import ChatService
from app.domain.chat.repository import ChatRepository
from app.domain.chat.schema import ChatCreate, ChatOut


class TestChatServiceCreate:
    """Unit tests for ChatService.create() method."""
    
    async def test_create_chat_success(
        self,
        db_session,
        test_user,  # Real user from DB
        mock_openai_manager
    ):
        """Test successful chat creation with real user."""
        # Arrange
        repo = ChatRepository()
        service = ChatService(
            db=db_session,
            repo=repo,
            user=test_user,
            manager=mock_openai_manager
        )
        
        chat_data = ChatCreate(
            name="Test Chat",
            user_id=test_user.id,
        )
        
        # Act
        result = await service.create(chat_data)
        
        # Assert
        assert result is not None
        assert isinstance(result, ChatOut)
        assert result.name == "Test Chat"
        assert result.user_id == test_user.id
        assert result.session_handle == "test_session_handle_123"
        
        # Verify OpenAI manager was called with correct user ID
        mock_openai_manager.create_conversation.assert_called_once_with(
            test_user.id
        )
