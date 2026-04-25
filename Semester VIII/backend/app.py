from flask import Flask, request, jsonify, send_from_directory
from core.chatbot_core import ask
from pathlib import Path
from flask import Flask, jsonify, request
import asyncio
from core.scraper_service import ScraperService
from core.csv_agent import CSVAgent
from datetime import datetime
from flask_cors import CORS
from flask_apscheduler import APScheduler
import json
from pathlib import Path
from core.analytics_service import AnalyticsService

app = Flask(__name__, static_folder="frontend/build", static_url_path="")
CORS(app)
scheduler = APScheduler()
scraper_service = ScraperService()
analytics_service = AnalyticsService()

BASE_DIR = Path(__file__).parent
PDF_DIR = BASE_DIR / "data" / "pdfs"
SCRAPED_DIR = BASE_DIR / "data" / "scraped"

def run_automated_pipeline():
    print(f"[{datetime.now()}] Starting automated 3-day background scrape...")
    try:
        asyncio.run(scraper_service.scrape_99acres(pages=5))
        asyncio.run(scraper_service.scrape_housing(pages=5))
        print(f"[{datetime.now()}] Automated scrape completed successfully.")
    except Exception as e:
        print(f"[{datetime.now()}] Automated scrape failed: {e}")

@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.json
    question = data.get("question", "")
    answer, sources = ask(question)
    return jsonify({
        "answer": answer,
        "sources": [
            {
                "pdf": source["pdf"],
                "page": source["page"],
                "link": source["link"]
            }
            for source in sources
        ]
    })

@app.route('/api/properties/query', methods=['POST'])
def query_properties():
    data = request.json or {}
    query = data.get('query', '')
    max_results = data.get('max_results', 10)
    
    if not query:
        return jsonify({"success": False, "error": "Query is required"}), 400
    
    try:
        from core.csv_agent import CSVAgent
        
        if SCRAPED_DIR.exists():
            data_dir = str(SCRAPED_DIR)
        else:
            data_dir = "data/scraped"
        
        agent = CSVAgent(data_dir=data_dir)
        result = agent.query_properties(query, max_results)
        return jsonify(result)
    except Exception as e:
        print(f"Error in query_properties: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500
    
@app.route('/api/analytics/dashboard', methods=['GET'])
def get_analytics_dashboard():
    """Get comprehensive analytics for dashboard visualizations"""
    try:
        analytics = analytics_service.get_dashboard_analytics()
        if analytics is None:
            return jsonify({
                "success": False,
                "error": "No data available. Please run a scrape first."
            }), 404
        return jsonify(analytics)
    except Exception as e:
        print(f"Error in get_analytics_dashboard: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/pdfs/<path:filename>")
def serve_pdf(filename):
    try:
        return send_from_directory(PDF_DIR, filename)
    except FileNotFoundError:
        from flask import abort
        abort(404)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    if path.startswith('pdfs') or path.startswith('ask'):
        from flask import abort
        abort(404)
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/scrape/versions', methods=['GET'])
def get_versions():
    limit = request.args.get('limit', 10, type=int)
    versions = scraper_service.get_versions(limit)
    return jsonify({"versions": versions})

@app.route('/api/scrape/version/<version_id>', methods=['GET'])
def get_version(version_id):
    version = scraper_service.get_version_details(version_id)
    if version:
        return jsonify(version)
    return jsonify({"error": "Version not found"}), 404

@app.route('/api/scrape/99acres', methods=['POST'])
def scrape_99acres():
    data = request.json or {}
    pages = data.get('pages', 10)
    
    try:
        result = asyncio.run(scraper_service.scrape_99acres(pages))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/scrape/housing', methods=['POST'])
def scrape_housing():
    data = request.json or {}
    pages = data.get('pages', 7)
    
    try:
        result = asyncio.run(scraper_service.scrape_housing(pages))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/scrape/status', methods=['GET'])
def get_scraping_status():
    active_versions = [v for v in scraper_service.get_versions(5) 
                      if v.get('status') in ['running', 'pending']]
    return jsonify({
        "active_jobs": len(active_versions),
        "recent_jobs": active_versions
    })

@app.route('/api/rera/projects', methods=['GET'])
def get_rera_projects():
    """Get all registered RERA projects"""
    try:
        projects_path = Path(__file__).parent / 'data' / 'json' / 'registered_projects.json'
        with open(projects_path, 'r', encoding='utf-8') as f:
            projects = json.load(f)
        return jsonify(projects)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/rera/common-bank-account', methods=['GET'])
def get_common_bank_account():
    """Get common bank account issues"""
    try:
        file_path = Path(__file__).parent / 'data' / 'json' / 'common_bank_account.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/rera/completion-date', methods=['GET'])
def get_completion_date_issues():
    """Get completion date issues"""
    try:
        file_path = Path(__file__).parent / 'data' / 'json' / 'lapse_of_completion_date.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/rera/non-compliance-qpr', methods=['GET'])
def get_non_compliance_qpr():
    """Get QPR non-compliance issues"""
    try:
        file_path = Path(__file__).parent / 'data' / 'json' / 'non_compliance_qpr.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/rera/district-analytics', methods=['GET'])
def get_district_analytics():
    try:
        projects_path = Path(__file__).parent / 'data' / 'json' / 'registered_projects.json'
        common_account_path = Path(__file__).parent / 'data' / 'json' / 'common_bank_account.json'
        completion_date_path = Path(__file__).parent / 'data' / 'json' / 'lapse_of_completion_date.json'
        qpr_path = Path(__file__).parent / 'data' / 'json' / 'non_compliance_qpr.json'
        
        with open(projects_path, 'r', encoding='utf-8') as f:
            projects = json.load(f)
        
        with open(common_account_path, 'r', encoding='utf-8') as f:
            common_account = json.load(f)
        
        with open(completion_date_path, 'r', encoding='utf-8') as f:
            completion_date = json.load(f)
        
        with open(qpr_path, 'r', encoding='utf-8') as f:
            qpr = json.load(f)
        
        district_map = {}
        
        for project in projects:
            district = project.get('project_District', 'Unknown')
            if district not in district_map:
                district_map[district] = {
                    'district': district,
                    'total_projects': 0,
                    'common_bank_issues': 0,
                    'completion_date_issues': 0,
                    'qpr_issues': 0,
                    'projects': []
                }
            district_map[district]['total_projects'] += 1
            district_map[district]['projects'].append(project)
        
        for item in common_account:
            district = item.get('Project 1 - District') or item.get('Project 2 District') or 'Unknown'
            if district in district_map:
                district_map[district]['common_bank_issues'] += 1
        
        for item in completion_date:
            district = item.get('District', 'Unknown')
            if district in district_map:
                district_map[district]['completion_date_issues'] += 1
        
        for item in qpr:
            district = item.get('District', 'Unknown')
            if district in district_map:
                district_map[district]['qpr_issues'] += 1
        
        analytics = []
        for district_data in district_map.values():
            total_issues = (district_data['common_bank_issues'] + 
                          district_data['completion_date_issues'] + 
                          district_data['qpr_issues'])
            
            if district_data['total_projects'] > 0:
                risk_score = (total_issues / district_data['total_projects']) * 100
                compliance_score = max(40, 100 - (total_issues * 5))
            else:
                risk_score = 0
                compliance_score = 100
            
            analytics.append({
                **district_data,
                'risk_score': round(risk_score, 1),
                'compliance_score': round(compliance_score, 1)
            })
        
        analytics.sort(key=lambda x: x['compliance_score'], reverse=True)
        
        return jsonify(analytics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    scheduler.add_job(
        id='scheduled_pipeline', 
        func=run_automated_pipeline, 
        trigger='interval', 
        days=3,
    )
    scheduler.init_app(app)
    scheduler.start()
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)