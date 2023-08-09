"""유저 관련 api 모음"""

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi_sqlalchemy import db
from server_modules.route import FilterSQLAlchemyCRUDRouter
from server_modules.schema import ResultResponse
from server_modules.utils.auth_util import get_user
from server_modules.utils.crud_router_callback_util import get_user_by_request, factory_is_owner_of_item_and_admin, \
    factory_insert_owner_id, is_signin
from server_modules.utils.db_util import paginate, get_model

from models.board.board import BoardModel
from models.board.board_comment import BoardCommentModel
from models.board.board_like import BoardLikeModel

board11_router = APIRouter(tags=["Boards"])
board_router = APIRouter(tags=["Boards"])

owner_validate_callback = factory_is_owner_of_item_and_admin('writer_id')
insert_owner_callback = factory_insert_owner_id('writer_id')


def get_all_board_convert(_: Request, board: BoardModel, __=None):
    """
    비밀 글일 경우 제목을 비밀로 처리
    content는 get_all일 경우 exclude로 처리
    """
    if board.secret:
        board.title = "secret title"
    board.like_count = paginate(BoardLikeModel, filters_info="like==1,board_idx==" + str(board.idx), only_total=True)[
        'total']
    board.comment_count = paginate(BoardCommentModel, filters_info="board_idx==" + str(board.idx), only_total=True)[
        'total']
    board.dislike_count = \
        paginate(BoardLikeModel, filters_info="like==0,board_idx==" + str(board.idx), only_total=True)[
            'total']
    return board


def get_one_board_callback(request: Request, board: BoardModel, _=None):
    """
    get one일 경우 조회수 증가
    """

    # 관리자가 아니고 비밀글일 경우 패스워드가 일치하지 않으면 401 에러
    if board.secret and get_user_by_request(request).tier != 0:
        if request.query_params.get('password') != board.password:
            raise HTTPException(status_code=401, detail="password is not correct")
    board.like_count = paginate(BoardLikeModel, filters_info="like==1,board_idx==" + str(board.idx), only_total=True)[
        'total']
    board.comment_count = paginate(BoardCommentModel, filters_info="board_idx==" + str(board.idx), only_total=True)[
        'total']
    board.dislike_count = \
        paginate(BoardLikeModel, filters_info="like==0,board_idx==" + str(board.idx), only_total=True)[
            'total']
    board.view_count += 1
    db.session.commit()


def create_board_start_callback(request: Request, db_model: BoardModel, _=None):
    """
    게시글 생성 전 검증
    """
    user = get_user_by_request(request)
    # 유저가 공지사항을 작성할 경우 관리자가 아니면 401 에러
    if user.tier != 0 and db_model.notice:
        raise HTTPException(status_code=401, detail="notice can be created by admin only")
    if db_model.secret and (not db_model.password or len(db_model.password) != 4):
        raise HTTPException(status_code=400, detail={
            'code': 1,
            'msg': 'password is required and must be 4 digits'
        })
    db_model.writer = user


def update_board_before_callback(request: Request, db_model: BoardModel, _=None):
    """
    게시글 생성 전 검증
    """
    owner_validate_callback(request, db_model)
    user = get_user_by_request(request)
    # 유저가 공지사항을 작성할 경우 관리자가 아니면 401 에러
    if user.tier != 0 and db_model.notice:
        raise HTTPException(status_code=401, detail="notice can be created by admin only")
    if db_model.secret and (not db_model.password or len(db_model.password) != 4):
        raise HTTPException(status_code=400, detail={
            'code': 1,
            'msg': 'password is required and must be 4 digits'
        })


board_router.include_router(
    FilterSQLAlchemyCRUDRouter(db_model=BoardModel,
                               prefix='/boards',
                               get_all_route_convert=get_all_board_convert,
                               get_one_route_callback=get_one_board_callback,
                               create_route_start_callback=create_board_start_callback,
                               # get 외에는 로그인 필요
                               delete_one_route=[Depends(get_user)],
                               update_route=[Depends(get_user)],
                               update_route_before_callback=update_board_before_callback,
                               delete_one_route_before_callback=owner_validate_callback,
                               create_route=[Depends(get_user)],
                               delete_all_route=False), tags=["Boards"])


def get_all_board_comment_convert(request: Request, comment: BoardCommentModel):
    """
    비밀 댓글일 경우 내용을 비밀로 처리
    관리자나 작성자 혹은 글 작성자일 경우 내용을 볼 수 있음
    """
    board = comment.board

    if comment.secret:
        if is_signin(request):
            user = get_user_by_request(request)
            if user.tier == 0 or board.writer.id == user.id or comment.writer_id == user.id:
                return comment
        comment.content = 'secret comment'
    return comment


board_router.include_router(
    FilterSQLAlchemyCRUDRouter(
        db_model=BoardCommentModel,
        prefix='/boards/{board_idx}/comments',
        get_all_route_convert=get_all_board_comment_convert,
        # get 외에는 로그인 필요
        get_one_route=False,
        delete_one_route=[Depends(get_user)],
        update_route=[Depends(get_user)],
        create_route=[Depends(get_user)],
        create_route_start_callback=insert_owner_callback,
        update_route_before_callback=owner_validate_callback,
        delete_one_route_before_callback=owner_validate_callback,
        delete_all_route=False, tags=["Boards"]))


@board_router.delete('/boards/{board_idx}/likes')
def delete_like_board(board_idx: int, user=Depends(get_user)) -> ResultResponse[bool]:
    """
    게시글 좋아요
    """
    board = get_model(BoardModel, board_idx)
    if user.id == board.writer_id:
        raise HTTPException(status_code=400, detail="you can't like your own board")
    db.session.query(BoardLikeModel).filter(
        (BoardLikeModel.board_idx == board_idx) & (BoardLikeModel.user_id == user.id)).delete()
    db.session.commit()
    return ResultResponse(rs=True)


@board_router.post('/boards/{board_idx}/likes')
def like_board(board_idx: int, like: BoardLikeModel.CreateSchema(),
               user=Depends(get_user)) -> BoardLikeModel.GetSchema():
    """
    게시글 좋아요
    """
    board = get_model(BoardModel, board_idx)
    if user.id == board.writer_id:
        raise HTTPException(status_code=400, detail="you can't like your own board")
    db.session.query(BoardLikeModel).filter(
        (BoardLikeModel.board_idx == board_idx) & (BoardLikeModel.user_id == user.id)).delete()
    board_like = BoardLikeModel()
    board_like.board_idx = board_idx
    board_like.user_id = user.id
    board_like.like = like.like
    db.session.add(board_like)
    db.session.commit()
    return board_like
