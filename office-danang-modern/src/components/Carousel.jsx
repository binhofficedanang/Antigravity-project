import React, { useRef } from 'react';

export default function Carousel({ children }) {
  const trackRef = useRef(null);

  const scroll = (direction) => {
    if (trackRef.current) {
      const itemWidth = trackRef.current.clientWidth;
      trackRef.current.scrollBy({ left: direction * itemWidth, behavior: 'smooth' });
    }
  };

  return (
    <div className="carousel-wrapper" style={{ height: '100%' }}>
      <button className="carousel-btn left" onClick={() => scroll(-1)} aria-label="Previous">
        ❮
      </button>
      <div className="carousel-track" ref={trackRef} style={{ height: '100%' }}>
        {children}
      </div>
      <button className="carousel-btn right" onClick={() => scroll(1)} aria-label="Next">
        ❯
      </button>
    </div>
  );
}
