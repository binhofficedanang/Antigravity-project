import React, { useState, useMemo, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet';
import { Link } from 'react-router-dom';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { geoData } from '../data/geo';

const defaultIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const activeIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// Calculate distance using Haversine formula (in km)
function getDistanceFromLatLonInKm(lat1, lon1, lat2, lon2) {
  const R = 6371; // Radius of the earth in km
  const dLat = (lat2 - lat1) * (Math.PI / 180);
  const dLon = (lon2 - lon1) * (Math.PI / 180);
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * (Math.PI / 180)) * Math.cos(lat2 * (Math.PI / 180)) * 
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
  return R * c;
}

const CENTER_POINTS = [
  { name: 'Cầu Rồng', lat: 16.061, lng: 108.227 },
  { name: 'Cầu Sông Hàn', lat: 16.071, lng: 108.224 },
  { name: 'Sân bay Quốc tế Đà Nẵng', lat: 16.054, lng: 108.202 },
  { name: 'Bến xe Trung tâm', lat: 16.052, lng: 108.170 }
];

// Helper component to control map panning and zooming
function MapController({ activeId, buildings, centerPoint, radiusKm, isRadiusMode }) {
  const map = useMap();
  
  useEffect(() => {
    if (activeId) {
      const b = buildings.find(x => x.id === activeId);
      if (b) {
        map.setView([b.lat, b.lng], 15, { animate: true });
      }
    }
  }, [activeId, buildings, map]);

  useEffect(() => {
    if (isRadiusMode) {
      map.setView([centerPoint.lat, centerPoint.lng], radiusKm <= 2 ? 14 : radiusKm <= 5 ? 13 : 12, { animate: true });
    }
  }, [centerPoint, radiusKm, isRadiusMode, map]);

  return null;
}

export default function MapView({ buildings, isRadiusMode, isHeatmapMode }) {
  const [centerPoint, setCenterPoint] = useState(CENTER_POINTS[0]);
  const [radiusKm, setRadiusKm] = useState(2);
  const [activeId, setActiveId] = useState(null);

  // Define colors based on price
  const getPriceColor = (price) => {
    if (!price || price === 0) return '#64748b'; // Gray for unknown
    if (price < 12) return '#10b981'; // Green for cheap
    if (price <= 18) return '#f59e0b'; // Orange/Yellow for medium
    return '#ef4444'; // Red for expensive
  };

  const displayBuildings = useMemo(() => {
    if (!isRadiusMode) return buildings;
    return buildings.filter(b => {
      const bLat = Number(b.lat || geoData[b.id]?.lat || 16.060);
      const bLng = Number(b.lng || geoData[b.id]?.lng || 108.220);
      const dist = getDistanceFromLatLonInKm(centerPoint.lat, centerPoint.lng, bLat, bLng);
      return dist <= radiusKm;
    });
  }, [buildings, isRadiusMode, centerPoint, radiusKm]);

  const mapCenter = isRadiusMode ? [centerPoint.lat, centerPoint.lng] : [16.060, 108.220];
  const mapZoom = isRadiusMode ? (radiusKm <= 2 ? 14 : radiusKm <= 5 ? 13 : 12) : 13;

  return (
    <div className="map-view-layout" style={{ 
      display: 'flex', 
      height: '650px', 
      background: '#fff', 
      borderRadius: '12px', 
      overflow: 'hidden', 
      border: '1px solid #eee',
      boxShadow: '0 4px 20px rgba(0,0,0,0.05)',
      marginTop: 20
    }}>
      
      {/* Left Sidebar: List of filtered buildings */}
      <div className="map-sidebar" style={{ 
        width: '35%', 
        overflowY: 'auto', 
        padding: '20px', 
        borderRight: '1px solid #eee',
        background: '#fafbfd'
      }}>
        <h3 style={{ margin: '0 0 16px 0', fontSize: '1.15rem', fontWeight: 'bold', color: '#2c3e50', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Danh sách tòa nhà</span>
          <span style={{ fontSize: '0.85rem', background: '#e31c5f', color: '#fff', padding: '2px 8px', borderRadius: '12px' }}>
            {displayBuildings.length} tòa
          </span>
        </h3>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {displayBuildings.map((b) => (
            <div 
              key={b.id} 
              onMouseEnter={() => setActiveId(b.id)}
              onMouseLeave={() => setActiveId(null)}
              style={{
                border: activeId === b.id ? '1px solid #e31c5f' : '1px solid #e2e8f0',
                boxShadow: activeId === b.id ? '0 4px 12px rgba(227, 28, 95, 0.06)' : 'none',
                borderRadius: '8px',
                padding: '12px',
                display: 'flex',
                gap: '12px',
                transition: 'all 0.2s',
                cursor: 'pointer',
                background: activeId === b.id ? '#fff9fa' : '#fff'
              }}
            >
              <img 
                src={b.image || b.imageUrl || '/assets/modern_office_generic.jpg'} 
                alt={b.name} 
                style={{ width: '70px', height: '70px', objectFit: 'cover', borderRadius: '6px' }} 
              />
              <div style={{ flex: 1, minWidth: 0 }}>
                <h4 style={{ margin: '0 0 4px 0', fontSize: '0.9rem', fontWeight: 'bold', color: '#2c3e50', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {b.name}
                </h4>
                <p style={{ margin: '0 0 6px 0', fontSize: '0.75rem', color: '#666', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  📍 {b.address}
                </p>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#e31c5f', fontWeight: 'bold', fontSize: '0.85rem' }}>${b.price}/m²</span>
                  <Link to={`/van-phong/${b.id}`} style={{ fontSize: '0.8rem', color: '#2563eb', textDecoration: 'none', fontWeight: 600 }}>Chi tiết →</Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right Map Content */}
      <div className="map-content" style={{ flex: 1, position: 'relative', height: '100%' }}>
        {isRadiusMode && (
          <div className="radius-control-panel" style={{
            position: 'absolute', top: 10, right: 10, zIndex: 1000, 
            background: 'white', padding: '16px', borderRadius: '8px', 
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)', minWidth: 260
          }}>
            <h3 style={{ margin: '0 0 12px 0', fontSize: '1rem', fontWeight: 'bold' }}>Lọc theo bán kính</h3>
            
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', fontSize: '0.8rem', color: '#666', marginBottom: 4 }}>Tâm điểm:</label>
              <select 
                value={centerPoint.name}
                onChange={(e) => {
                  const p = CENTER_POINTS.find(x => x.name === e.target.value);
                  if (p) setCenterPoint(p);
                }}
                style={{ width: '100%', padding: '6px', borderRadius: '4px', border: '1px solid #ddd', fontSize: '0.85rem' }}
              >
                {CENTER_POINTS.map(p => (
                  <option key={p.name} value={p.name}>{p.name}</option>
                ))}
                {centerPoint.name.includes('Tùy chỉnh') && (
                  <option value={centerPoint.name}>{centerPoint.name}</option>
                )}
              </select>
            </div>

            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#666', marginBottom: 4 }}>
                <span>Bán kính:</span>
                <strong>{radiusKm} km</strong>
              </label>
              <input 
                type="range" 
                min="1" max="10" step="0.5" 
                value={radiusKm}
                onChange={(e) => setRadiusKm(Number(e.target.value))}
                style={{ width: '100%' }}
              />
            </div>
            
            <div style={{ fontSize: '0.8rem', color: '#e31c5f', fontWeight: 'bold' }}>
              Tìm thấy {displayBuildings.length} tòa nhà
            </div>
          </div>
        )}

        <MapContainer center={mapCenter} zoom={mapZoom} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          
          <MapController 
            activeId={activeId} 
            buildings={displayBuildings} 
            centerPoint={centerPoint} 
            radiusKm={radiusKm} 
            isRadiusMode={isRadiusMode} 
          />

          {isRadiusMode && (
            <Circle 
              center={[centerPoint.lat, centerPoint.lng]} 
              radius={radiusKm * 1000} 
              pathOptions={{ fillColor: '#e31c5f', fillOpacity: 0.08, color: '#e31c5f', weight: 1.5 }} 
            />
          )}

          {isRadiusMode && (
             <Marker 
               icon={defaultIcon}
               position={[centerPoint.lat, centerPoint.lng]}
               draggable={true}
               eventHandlers={{
                 dragend: (e) => {
                   const pos = e.target.getLatLng();
                   setCenterPoint({ name: 'Tùy chỉnh (Kéo thả)', lat: pos.lat, lng: pos.lng });
                 }
               }}
             >
               <Popup><strong>{centerPoint.name}</strong><br/>Kéo thả ghim này để đổi tâm điểm</Popup>
             </Marker>
          )}

          {displayBuildings.map((b) => {
            const priceVal = parseFloat(b.price) || 0;
            const hColor = getPriceColor(priceVal);

            if (isHeatmapMode) {
              return (
                <Circle 
                  key={b.id} 
                  center={[b.lat, b.lng]} 
                  radius={150} // 150 meters
                  pathOptions={{ fillColor: hColor, fillOpacity: 0.7, color: hColor, weight: 2 }}
                  eventHandlers={{
                    mouseover: () => setActiveId(b.id),
                    mouseout: () => setActiveId(null)
                  }}
                >
                  <Popup>
                    <div style={{ width: 180 }}>
                      <img 
                        src={b.image || b.imageUrl || '/assets/modern_office_generic.jpg'} 
                        alt={b.name} 
                        style={{ width: '100%', height: 100, objectFit: 'cover', borderRadius: 4, marginBottom: 8 }} 
                      />
                      <h4 style={{ margin: '0 0 4px 0', fontSize: '0.9rem', fontWeight: 'bold' }}>{b.name}</h4>
                      <p style={{ margin: '0 0 8px 0', fontSize: '0.75rem', color: '#666' }}>{b.address}</p>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ color: hColor, fontWeight: 'bold', fontSize: '0.95rem' }}>${priceVal > 0 ? priceVal : 'Liên hệ'}</span>
                        <Link to={`/van-phong/${b.id}`} style={{ background: '#333', color: '#fff', padding: '3px 8px', borderRadius: 4, textDecoration: 'none', fontSize: '0.75rem' }}>Chi tiết</Link>
                      </div>
                    </div>
                  </Popup>
                </Circle>
              );
            }

            return (
              <Marker 
                key={b.id} 
                position={[b.lat, b.lng]} 
                icon={activeId === b.id ? activeIcon : defaultIcon}
                eventHandlers={{
                  mouseover: () => setActiveId(b.id),
                  mouseout: () => setActiveId(null)
                }}
              >
                <Popup>
                  <div style={{ width: 180 }}>
                    <img 
                      src={b.image || b.imageUrl || '/assets/modern_office_generic.jpg'} 
                      alt={b.name} 
                      style={{ width: '100%', height: 100, objectFit: 'cover', borderRadius: 4, marginBottom: 8 }} 
                    />
                    <h4 style={{ margin: '0 0 4px 0', fontSize: '0.9rem', fontWeight: 'bold' }}>{b.name}</h4>
                    <p style={{ margin: '0 0 8px 0', fontSize: '0.75rem', color: '#666' }}>{b.address}</p>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ color: '#e31c5f', fontWeight: 'bold', fontSize: '0.85rem' }}>${b.price}/m²</span>
                      <Link to={`/van-phong/${b.id}`} style={{ background: '#333', color: '#fff', padding: '3px 8px', borderRadius: 4, textDecoration: 'none', fontSize: '0.75rem' }}>Chi tiết</Link>
                    </div>
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>
    </div>
  );
}
