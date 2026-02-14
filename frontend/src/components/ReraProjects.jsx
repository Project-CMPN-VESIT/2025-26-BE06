import { useState, useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import '../styles/ReraProjects.css';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

function ReraProjects() {
  const [projects, setProjects] = useState([]);
  const [nonRegisteredProjects, setNonRegisteredProjects] = useState([]);
  const [selectedDistrict, setSelectedDistrict] = useState(null);
  const [districtAnalytics, setDistrictAnalytics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  
  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const [projectsPerPage] = useState(20);
  const [nonRegCurrentPage, setNonRegCurrentPage] = useState(1);
  const [nonRegPerPage] = useState(20);

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      const [projectsRes, commonAccountRes, completionDateRes, qprRes] = await Promise.all([
        fetch('/api/rera/projects'),
        fetch('/api/rera/common-bank-account'),
        fetch('/api/rera/completion-date'),
        fetch('/api/rera/non-compliance-qpr')
      ]);

      if (!projectsRes.ok) throw new Error('Failed to fetch projects data');
      
      const projectsData = await projectsRes.json();
      const commonAccountData = await commonAccountRes.json();
      const completionDateData = await completionDateRes.json();
      const qprData = await qprRes.json();

      // Extract non-registered projects from compliance data
      const nonRegistered = [
        ...commonAccountData.map(item => ({
          type: 'Common Bank Account',
          projectName: item['Name of Project 1'],
          certificateNo: item['Project 1 - Certificate No.'],
          district: item['Project 1 - District'],
          promoter: item['Name of Promoter'],
          issue: 'Multiple projects under same bank account'
        })),
        ...completionDateData.map(item => ({
          type: 'Lapsed Completion Date',
          projectName: item['Name of Project'],
          certificateNo: item['Certificate No.'],
          district: item.District,
          promoter: item['Name of Promoter'],
          issue: 'Missing completion date'
        })),
        ...qprData.map(item => ({
          type: 'QPR Non-Compliance',
          projectName: item['Project Name'],
          certificateNo: item['Certificate Number'],
          district: item.District,
          promoter: item['Promoter Name'],
          issue: `Non-compliance in ${item.Month} ${item.Year}`
        }))
      ];

      setProjects(projectsData);
      setNonRegisteredProjects(nonRegistered);
      calculateDistrictAnalytics(projectsData, commonAccountData, completionDateData, qprData);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateDistrictAnalytics = (projects, commonAccount, completionDate, qpr) => {
    const districtMap = {};
    
    // Count total projects per district
    projects.forEach(project => {
      const district = project.project_District || 'Unknown';
      if (!districtMap[district]) {
        districtMap[district] = {
          district,
          totalProjects: 0,
          totalIssues: 0,
          projectDensity: 0,
          avgProjectAge: 0,
          complianceRate: 0,
          projects: []
        };
      }
      districtMap[district].totalProjects++;
      districtMap[district].projects.push(project);
    });

    // Count issues per district
    const countIssues = (data, districtField) => {
      data.forEach(item => {
        const district = item[districtField] || 'Unknown';
        if (districtMap[district]) {
          districtMap[district].totalIssues++;
        }
      });
    };

    countIssues(commonAccount, 'Project 1 - District');
    countIssues(completionDate, 'District');
    countIssues(qpr, 'District');

    // Calculate metrics
    Object.values(districtMap).forEach(district => {
      // Calculate project density score (higher = more projects per area)
      district.projectDensity = district.totalProjects;
      
      // Calculate compliance rate
      if (district.totalProjects > 0) {
        district.complianceRate = Math.max(0, 100 - ((district.totalIssues / district.totalProjects) * 100));
      }
      
      // Calculate investment attractiveness score
      district.investmentScore = calculateInvestmentScore(district);
    });

    const analytics = Object.values(districtMap).map(district => ({
      ...district,
      investmentScore: district.investmentScore || 0,
      complianceRate: district.complianceRate || 0,
      totalIssues: district.totalIssues || 0
    }));

    setDistrictAnalytics(analytics.sort((a, b) => b.investmentScore - a.investmentScore));
  };

  const calculateInvestmentScore = (district) => {
    let score = 50; // Base score
    
    // Higher project density = higher score
    score += Math.min(district.totalProjects * 0.5, 30);
    
    // Lower issues = higher score
    if (district.totalProjects > 0) {
      const issueRatio = district.totalIssues / district.totalProjects;
      score += (1 - issueRatio) * 20;
    }
    
    return Math.round(Math.min(Math.max(score, 0), 100));
  };

  const getInvestmentRating = (score) => {
    if (score >= 80) return { label: 'Premium', className: 'rating-premium' };
    if (score >= 70) return { label: 'High', className: 'rating-high' };
    if (score >= 60) return { label: 'Moderate', className: 'rating-moderate' };
    if (score >= 50) return { label: 'Fair', className: 'rating-fair' };
    return { label: 'Low', className: 'rating-low' };
  };

  const filteredProjects = useMemo(() => {
    return selectedDistrict 
      ? projects.filter(p => p.project_District === selectedDistrict)
      : projects;
  }, [selectedDistrict, projects]);

  const filteredNonRegistered = useMemo(() => {
    return selectedDistrict
      ? nonRegisteredProjects.filter(p => p.district === selectedDistrict)
      : nonRegisteredProjects;
  }, [selectedDistrict, nonRegisteredProjects]);

  // Pagination logic for registered projects
  const indexOfLastProject = currentPage * projectsPerPage;
  const indexOfFirstProject = indexOfLastProject - projectsPerPage;
  const currentProjects = filteredProjects.slice(indexOfFirstProject, indexOfLastProject);
  const totalPages = Math.ceil(filteredProjects.length / projectsPerPage);

  // Pagination logic for non-registered projects
  const indexOfLastNonReg = nonRegCurrentPage * nonRegPerPage;
  const indexOfFirstNonReg = indexOfLastNonReg - nonRegPerPage;
  const currentNonRegProjects = filteredNonRegistered.slice(indexOfFirstNonReg, indexOfLastNonReg);
  const totalNonRegPages = Math.ceil(filteredNonRegistered.length / nonRegPerPage);

  const centerCoords = useMemo(() => {
    if (filteredProjects.length === 0) return [19.0760, 72.8777];
    const lats = filteredProjects.map(p => parseFloat(p.Latitude)).filter(lat => !isNaN(lat));
    const lons = filteredProjects.map(p => parseFloat(p.Longitude)).filter(lon => !isNaN(lon));
    if (lats.length === 0 || lons.length === 0) return [19.0760, 72.8777];
    return [
      lats.reduce((a, b) => a + b) / lats.length,
      lons.reduce((a, b) => a + b) / lons.length
    ];
  }, [filteredProjects]);

  const paginate = (pageNumber) => setCurrentPage(pageNumber);
  const paginateNonReg = (pageNumber) => setNonRegCurrentPage(pageNumber);

  const handleDistrictClick = (district) => {
    setSelectedDistrict(district === selectedDistrict ? null : district);
    setCurrentPage(1);
    setNonRegCurrentPage(1);
  };

  if (loading) {
    return (
      <div className="rera-loading-container">
        <div className="rera-loading-spinner"></div>
        <div className="rera-loading-text">Loading RERA Analytics Dashboard</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rera-error-container">
        <div className="rera-error-message">Error Loading Dashboard Data</div>
        <button onClick={fetchAllData} className="rera-retry-button">Retry</button>
      </div>
    );
  }

  return (
    <div className="rera-dashboard">
      <div className="dashboard-header">
        <div className="header-content">
          <h1 className="dashboard-title">RERA Projects Intelligence Dashboard</h1>
          <p className="dashboard-subtitle">
            Maharashtra Real Estate Regulatory Authority - Registered Projects Analysis
          </p>
        </div>
      </div>

      <div className="map-section">
        <div className="section-header">
          <h2 className="section-title">Registered Projects Map</h2>
          <p className="section-subtitle">
            {selectedDistrict ? `Showing projects in ${selectedDistrict}` : 'All registered RERA projects across Maharashtra'}
            {filteredProjects.length > 0 && ` • ${filteredProjects.length.toLocaleString()} projects`}
          </p>
        </div>
        <div className="map-container-wrapper">
          <MapContainer
            center={centerCoords}
            zoom={selectedDistrict ? 12 : 8}
            className="rera-map"
          >
            <TileLayer
              url="http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
              attribution='&copy; OpenStreetMap contributors'
            />
            {filteredProjects
              .filter(p => p.Latitude && p.Longitude)
              .slice(0, 1000) // Limit markers for performance
              .map((project, index) => (
                <Marker
                  key={index}
                  position={[parseFloat(project.Latitude), parseFloat(project.Longitude)]}
                  eventHandlers={{
                    click: () => setSelectedProject(project)
                  }}
                >
                  <Popup>
                    <div className="project-popup">
                      <h3 className="popup-title">{project.projectName}</h3>
                      <p className="popup-location">{project.locality}, {project.project_District}</p>
                      <p className="popup-certificate">
                        Certificate: <a 
                          href={`https://maharera.maharashtra.gov.in/projects-search-result?project-number=${project.CertificateNo}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="certificate-link"
                        >
                          {project.CertificateNo}
                        </a>
                      </p>
                    </div>
                  </Popup>
                </Marker>
              ))}
          </MapContainer>
        </div>
      </div>

      <div className="analytics-section">
        <div className="section-header">
          <h2 className="section-title">District Investment Analysis</h2>
          <p className="section-subtitle">
            Market attractiveness assessment by district
          </p>
        </div>
        
        <div className="district-grid">
          <div className="district-grid-header">
            <div className="grid-column">District</div>
            <div className="grid-column">Total Projects</div>
            <div className="grid-column">Total Issues</div>
            <div className="grid-column">Investment Score</div>
            <div className="grid-column">Market Rating</div>
          </div>
          
          {districtAnalytics.map((district, index) => {
            const rating = getInvestmentRating(district.investmentScore);
            return (
              <div
                key={index}
                className={`district-row ${selectedDistrict === district.district ? 'selected' : ''}`}
                onClick={() => handleDistrictClick(district.district)}
              >
                <div className="grid-column">
                  <div className="district-name">{district.district}</div>
                </div>
                <div className="grid-column">
                  <div className="district-value">{district.totalProjects.toLocaleString()}</div>
                  <div className="district-subtext">Registered</div>
                </div>
                <div className="grid-column">
                  <div className="district-value">{district.totalIssues}</div>
                  <div className="district-subtext">Compliance Issues</div>
                </div>
                <div className="grid-column">
                  <div className="score-container">
                    <div className="score-bar">
                      <div 
                        className="score-fill" 
                        style={{ width: `${district.investmentScore}%` }}
                      />
                    </div>
                    <span className="score-value">{district.investmentScore}</span>
                  </div>
                </div>
                <div className="grid-column">
                  <span className={`rating-badge ${rating.className}`}>
                    {rating.label}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {selectedDistrict && (
        <>
          <div className="detail-section">
            <div className="section-header">
              <h2 className="section-title">{selectedDistrict} - Registered Projects</h2>
              <p className="section-subtitle">
                Showing {currentProjects.length} of {filteredProjects.length} projects
              </p>
            </div>
            
            <div className="projects-table">
              <div className="table-header">
                <div className="table-column">Project Name</div>
                <div className="table-column">Locality</div>
                <div className="table-column">Certificate No.</div>
                <div className="table-column">Address</div>
                <div className="table-column">Coordinates</div>
              </div>
              
              {currentProjects.length > 0 ? (
                <>
                  {currentProjects.map((project, index) => (
                    <div key={index} className="table-row">
                      <div className="table-column">
                        <div className="project-name">{project.projectName}</div>
                      </div>
                      <div className="table-column">
                        <div className="project-locality">{project.locality}</div>
                        <div className="project-taluka">{project.project_Taluka}</div>
                      </div>
                      <div className="table-column">
                        <a 
                          href={`https://maharera.maharashtra.gov.in/projects-search-result?project-number=${project.CertificateNo}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="certificate-link"
                        >
                          {project.CertificateNo}
                        </a>
                      </div>
                      <div className="table-column">
                        <div className="project-address">
                          {project.street}, {project.project_Village}
                          <div className="project-pincode">Pincode: {project.pincode}</div>
                        </div>
                      </div>
                      <div className="table-column">
                        <div className="project-coordinates">
                          {parseFloat(project.Latitude).toFixed(6)}, {parseFloat(project.Longitude).toFixed(6)}
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {filteredProjects.length > projectsPerPage && (
                    <div className="pagination-controls">
                      <button
                        onClick={() => paginate(currentPage - 1)}
                        disabled={currentPage === 1}
                        className="pagination-button"
                      >
                        Previous
                      </button>
                      <span className="pagination-info">
                        Page {currentPage} of {totalPages}
                      </span>
                      <button
                        onClick={() => paginate(currentPage + 1)}
                        disabled={currentPage === totalPages}
                        className="pagination-button"
                      >
                        Next
                      </button>
                    </div>
                  )}
                </>
              ) : (
                <div className="no-data-message">No registered projects found in this district</div>
              )}
            </div>
          </div>

          <div className="non-registered-section">
            <div className="section-header">
              <h2 className="section-title">{selectedDistrict} - Compliance Issues</h2>
              <p className="section-subtitle">
                Projects with regulatory compliance concerns
              </p>
            </div>
            
            <div className="projects-table">
              <div className="table-header">
                <div className="table-column">Issue Type</div>
                <div className="table-column">Project Name</div>
                <div className="table-column">Promoter</div>
                <div className="table-column">Certificate No.</div>
                <div className="table-column">Issue Details</div>
              </div>
              
              {currentNonRegProjects.length > 0 ? (
                <>
                  {currentNonRegProjects.map((project, index) => (
                    <div key={index} className="table-row non-registered">
                      <div className="table-column">
                        <span className={`issue-type ${project.type.toLowerCase().replace(/ /g, '-')}`}>
                          {project.type}
                        </span>
                      </div>
                      <div className="table-column">
                        <div className="project-name">{project.projectName}</div>
                      </div>
                      <div className="table-column">
                        <div className="project-promoter">{project.promoter}</div>
                      </div>
                      <div className="table-column">
                        {project.certificateNo ? (
                          <a 
                            href={`https://maharera.maharashtra.gov.in/projects-search-result?project-number=${project.certificateNo}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="certificate-link"
                          >
                            {project.certificateNo}
                          </a>
                        ) : (
                          <span className="no-certificate">Not Available</span>
                        )}
                      </div>
                      <div className="table-column">
                        <div className="issue-details">{project.issue}</div>
                      </div>
                    </div>
                  ))}
                  
                  {filteredNonRegistered.length > nonRegPerPage && (
                    <div className="pagination-controls">
                      <button
                        onClick={() => paginateNonReg(nonRegCurrentPage - 1)}
                        disabled={nonRegCurrentPage === 1}
                        className="pagination-button"
                      >
                        Previous
                      </button>
                      <span className="pagination-info">
                        Page {nonRegCurrentPage} of {totalNonRegPages}
                      </span>
                      <button
                        onClick={() => paginateNonReg(nonRegCurrentPage + 1)}
                        disabled={nonRegCurrentPage === totalNonRegPages}
                        className="pagination-button"
                      >
                        Next
                      </button>
                    </div>
                  )}
                </>
              ) : (
                <div className="no-data-message">No compliance issues found in this district</div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default ReraProjects;