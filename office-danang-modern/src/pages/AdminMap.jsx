import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { supabase, fetchBuildings } from '../utils/api';

import 'leaflet/dist/leaflet.css';

// Fix leafet default icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom icon for dragged/unsaved pins
const unsavedIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const defaultIcon = new L.Icon.Default();

function AdminMap() {
  const [buildings, setBuildings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [savingStatus, setSavingStatus] = useState('');
  
  // Track changed coordinates
  const [changedCoords, setChangedCoords] = useState({});

  useEffect(() => {
    loadBuildings();
  }, []);

  const loadBuildings = async () => {
    setLoading(true);
    try {
      const data = await fetchBuildings();
      setBuildings(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDragEnd = (id, event) => {
    const marker = event.target;
    const position = marker.getLatLng();
    setChangedCoords(prev => ({
      ...prev,
      [id]: { lat: position.lat, lng: position.lng }
    }));
  };

  const saveCoordinate = async (id, name) => {
    const coords = changedCoords[id];
    if (!coords) return;
    
    setSavingStatus(`Đang lưu tọa độ cho ${name}...`);
    
    try {
      const { error } = await supabase
        .from('buildings')
        .update({ lat: coords.lat, lng: coords.lng })
        .eq('id', id);
        
      if (error) throw error;
      
      setSavingStatus(`Đã lưu thành công cho ${name}!`);
      
      // Update local state and remove from changed
      setBuildings(prev => prev.map(b => b.id === id ? { ...b, lat: coords.lat, lng: coords.lng } : b));
      setChangedCoords(prev => {
        const newCoords = { ...prev };
        delete newCoords[id];
        return newCoords;
      });
      
      setTimeout(() => setSavingStatus(''), 3000);
    } catch (err) {
      console.error(err);
      setSavingStatus(`Lỗi khi lưu: ${err.message}`);
    }
  };

  if (loading) return <div style={{ padding: '100px', textAlign: 'center' }}>Đang tải bản đồ...</div>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <div style={{ padding: '20px', background: '#fff', borderBottom: '1px solid #ddd', zIndex: 1000, position: 'relative' }}>
        <h1 style={{ margin: '0 0 10px 0', fontSize: '24px' }}>Trang Quản Trị Tọa Độ Bản Đồ</h1>
        <p style={{ margin: '0 0 10px 0', color: '#666' }}>
          <strong>Hướng dẫn:</strong> Kéo thả các ghim màu xanh trên bản đồ đến vị trí chính xác. Khi thả ra, ghim sẽ chuyển sang <strong style={{color: 'red'}}>màu đỏ</strong>. Bấm vào ghim màu đỏ và chọn <strong>"Lưu vị trí mới"</strong> để lưu vào cơ sở dữ liệu Supabase.
        </p>
        {savingStatus && (
          <div style={{ padding: '10px', background: savingStatus.includes('Lỗi') ? '#ffebee' : '#e8f5e9', color: savingStatus.includes('Lỗi') ? '#c62828' : '#2e7d32', borderRadius: '4px', fontWeight: 'bold' }}>
            {savingStatus}
          </div>
        )}
      </div>

      <div style={{ flex: 1, position: 'relative' }}>
        <MapContainer 
          center={[16.060, 108.220]} 
          zoom={14} 
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; OpenStreetMap contributors"
          />
          {buildings.map(b => {
            const hasChanged = changedCoords[b.id];
            const currentLat = hasChanged ? hasChanged.lat : b.lat;
            const currentLng = hasChanged ? hasChanged.lng : b.lng;
            
            // Skip rendering if no valid coordinates
            if (!currentLat || !currentLng) return null;

            return (
              <Marker 
                key={b.id} 
                position={[currentLat, currentLng]}
                draggable={true}
                eventHandlers={{
                  dragend: (e) => handleDragEnd(b.id, e)
                }}
                icon={hasChanged ? unsavedIcon : defaultIcon}
              >
                <Popup>
                  <div style={{ textAlign: 'center' }}>
                    <strong style={{ display: 'block', marginBottom: '8px' }}>{b.name}</strong>
                    <div style={{ fontSize: '12px', color: '#666', marginBottom: '10px' }}>
                      {b.address}
                    </div>
                    {hasChanged ? (
                      <div>
                        <p style={{ margin: '0 0 10px 0', color: '#d32f2f', fontSize: '12px' }}>Chưa lưu vị trí mới!</p>
                        <button 
                          onClick={() => saveCoordinate(b.id, b.name)}
                          style={{
                            background: '#1976d2',
                            color: '#fff',
                            border: 'none',
                            padding: '6px 12px',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            width: '100%'
                          }}
                        >
                          Lưu vị trí mới
                        </button>
                      </div>
                    ) : (
                      <div style={{ fontSize: '12px', color: '#2e7d32' }}>Đã đồng bộ</div>
                    )}
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

export default AdminMap;
