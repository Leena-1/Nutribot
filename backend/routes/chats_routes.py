from fastapi import APIRouter, HTTPException

from backend.schemas.chat import ChatQueryRequest, ChatQueryResponse
from backend.services.chat_service import chat_response_async

router = APIRouter()


@router.post("/chat_query", response_model=ChatQueryResponse)
async def chat_query(body: ChatQueryRequest) -> ChatQueryResponse:

    try:
        reply = await chat_response_async(
            body.query,
            user_context=body.user_context,
            user_id=body.user_id
        )

        return ChatQueryResponse(
            query=body.query,
            response=reply
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
