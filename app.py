from fastapi import *
from fastapi.responses import FileResponse, JSONResponse,HTMLResponse
import uvicorn
import mysql.connector 
from mysql.connector import errors
from datetime import date, datetime, timedelta
import decimal
from typing import Optional
import json
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app=FastAPI()
app.mount("/week1secondface", StaticFiles(directory="html"), name="static")
templates = Jinja2Templates(directory="html")


def connect_to_db():
    return mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678",
    database="attractions"
)
def serialize_data(data):#讓資料可以換成json
    
    for key, value in data.items():
        if isinstance(value, (date, datetime)):
            data[key] = value.isoformat()
        elif isinstance(value, decimal.Decimal):
            data[key] = float(value)
    return data

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@app.get("/attraction/{attractionId}", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("attractionpage.html", {"request": request})

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")


@app.get("/api/attractions")
async def getattractions(request: Request, page: int = Query(..., ge=0), keyword: str = Query(None)):
    try:
        db_connection = connect_to_db()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")
    
    try:
        cursor = db_connection.cursor(dictionary=True)
        item_per_page = 12
        offset = page * item_per_page
        like_keyword = f"%{keyword}%" if keyword else None
        #抓出總共有多少向，用在後面的exception
        count_query = "SELECT COUNT(*) as total FROM attractions"
        cursor.execute(count_query)
        total_items = cursor.fetchone()["total"]
        count_query_keyword = """
            SELECT COUNT(*) as total
            FROM attractions a 
            JOIN categories c ON a.category_id = c.id 
            JOIN mrt_stations m ON a.mrt_id = m.id 
            WHERE a.name LIKE %s OR m.name LIKE %s"""
        cursor.execute(count_query_keyword, (like_keyword,like_keyword))
        total_items_keyword = cursor.fetchone()["total"]
        if keyword:
            query = """
            SELECT 
                a.id,
                a.name,
                c.name AS category,
                a.description,
                a.address,
                a.direction AS transport,
                m.name AS mrt,
                a.latitude AS lat,
                a.longitude AS lng,
                a.file AS images
            FROM 
                attractions a
            JOIN 
                categories c ON a.category_id = c.id
            JOIN 
                mrt_stations m ON a.mrt_id = m.id
            WHERE a.name LIKE %s OR m.name LIKE %s
            ORDER BY
                a.id
            LIMIT %s OFFSET %s
            """
            cursor.execute(query, (like_keyword, like_keyword, item_per_page, offset))
        else:
            query = """
            SELECT 
                a.id,
                a.name,
                c.name AS category,
                a.description,
                a.address,
                a.direction AS transport,
                m.name AS mrt,
                a.latitude AS lat,
                a.longitude AS lng,
                a.file AS images
            FROM 
                attractions a
            JOIN 
                categories c ON a.category_id = c.id
            JOIN 
                mrt_stations m ON a.mrt_id = m.id
            ORDER BY
                a.id
            LIMIT %s OFFSET %s
            """
            cursor.execute(query, (item_per_page, offset))
        
        data = cursor.fetchall()
        if not keyword:
            nextPage = page + 1 if total_items > offset + item_per_page else None
        else:
            nextPage = page +1 if total_items_keyword > offset + item_per_page else None
        if not data:
            raise HTTPException(status_code=400, detail="Wrong page number")
        
        # 確保 images 欄位是 JSON 格式
        for item in data:
            if item.get('images'):
                    item['images'] = json.loads(item['images'])
                
        
        return {'nextPage': nextPage, 'data': data}
    except errors.Error as e:
        raise HTTPException(status_code=500, detail="An error occurred while executing the query.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        db_connection.close()
@app.get("/api/attractions/{attractionId}")
async def attractionIdsearch(request: Request, attractionId: int):
    try:
        db_connection = connect_to_db()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")
    
    try:
        cursor = db_connection.cursor(dictionary=True)#這樣返回的結果會是一個字典，方便轉換為 JSON。
        cursor.execute( """
		SELECT 
			a.id,
			a.name,
            c.name AS category,
			a.description,
			a.address,
			a.direction As transport,
            m.name AS mrt,
            a.latitude As lat,
			a.longitude As lng,
			a.file As images
			
			
		FROM 
			attractions a
		JOIN 
			categories c ON a.category_id = c.id
		JOIN 
			mrt_stations m ON a.mrt_id = m.id
		WHERE 
			a.id = %s;
		""", (attractionId,))
        result = cursor.fetchone()
        cursor.close()
        db_connection.close()

        if result is None:
            raise HTTPException(status_code=400, detail="Wrong attraction ID")
        if result.get('images'):       
            result['images'] = json.loads(result['images'])

        result = serialize_data(result)  # 序列化日期和小數類型

        return JSONResponse(content={"data": result})
    except errors.Error as e:
        
        raise HTTPException(status_code=500, detail="An error occurred while executing the query.")
    except Exception as e:
        
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    

@app.get("/api/mrts")
async def SearchAllmrt(request: Request):
	try:
		db_connection = connect_to_db()
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")
		
	
	try:
		cursor = db_connection.cursor()
		cursor.execute("Select name from(Select mrt_stations.name, Count(attractions.mrt_id) as count from mrt_stations join attractions on mrt_stations.id = attractions.mrt_id group by mrt_stations.name order by count desc) as subquery")
		result = cursor.fetchall()
		cursor.close()
		db_connection.close()

		mrt_names = [row[0] for row in result]

		return JSONResponse(content={"data": mrt_names})
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"An error occurred while executing the query.: {e}")



