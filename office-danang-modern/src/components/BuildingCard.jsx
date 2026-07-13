import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useCompare } from '../context/CompareContext';

export default function BuildingCard({ building }) {
  const b = building;
  const slug = b.id;
  const { toggleCompare, isSelected } = useCompare();
  const selected = isSelected(b.id);

  return (
    <Link to={`/van-phong/${slug}`} className="building-card animate-fade-in">
      <div className="card-thumb">
        <img src={b.imageUrl || b.image} alt={b.name} loading="lazy" />
        <div 
          className={`compare-card-checkbox ${selected ? 'active' : ''}`}
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            toggleCompare(b);
          }}
          title={selected ? 'Xóa khỏi danh sách so sánh' : 'Chọn so sánh'}
        >
          <span className="compare-icon">{selected ? '✓' : '+'}</span> So sánh
        </div>
      </div>
      <div className="card-body">
        <h3>{b.name}</h3>
        <div className="card-address">{b.address.replace(/,\s*(Thành phố |TP\.?\s*)?Đà Nẵng/gi, '')}</div>

        <div className="card-price">
          {parseFloat(b.price) > 0 ? (
            <>
              ${parseFloat(b.price)} {parseFloat(b.serviceCharge) > 0 ? <span style={{fontSize: '0.85rem', color: '#64748b', fontWeight: 500}}>+ ${parseFloat(b.serviceCharge)} phí DV</span> : ''} <span className="unit">/ m²</span>
            </>
          ) : (
            "Liên hệ"
          )}
        </div>
      </div>
    </Link>
  );
}
