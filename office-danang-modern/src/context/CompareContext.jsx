import React, { createContext, useState, useContext, useEffect } from 'react';

const CompareContext = createContext();

export function CompareProvider({ children }) {
  const [selectedBuildings, setSelectedBuildings] = useState([]);

  // Load initial selections from sessionStorage if present
  useEffect(() => {
    const saved = sessionStorage.getItem('compare_buildings');
    if (saved) {
      try {
        setSelectedBuildings(JSON.parse(saved));
      } catch (e) {
        console.error('Error parsing sessionStorage compare_buildings:', e);
      }
    }
  }, []);

  const toggleCompare = (building) => {
    setSelectedBuildings((prev) => {
      const exists = prev.some((b) => b.id === building.id);
      let updated;
      if (exists) {
        updated = prev.filter((b) => b.id !== building.id);
      } else {
        if (prev.length >= 3) {
          alert('Bạn chỉ có thể so sánh tối đa 3 tòa nhà cùng lúc!');
          return prev;
        }
        updated = [...prev, building];
      }
      sessionStorage.setItem('compare_buildings', JSON.stringify(updated));
      return updated;
    });
  };

  const clearCompare = () => {
    setSelectedBuildings([]);
    sessionStorage.removeItem('compare_buildings');
  };

  const isSelected = (buildingId) => {
    return selectedBuildings.some((b) => b.id === buildingId);
  };

  return (
    <CompareContext.Provider value={{ selectedBuildings, toggleCompare, clearCompare, isSelected }}>
      {children}
    </CompareContext.Provider>
  );
}

export function useCompare() {
  const context = useContext(CompareContext);
  if (!context) {
    throw new Error('useCompare must be used within a CompareProvider');
  }
  return context;
}
