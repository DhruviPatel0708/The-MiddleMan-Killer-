/**
 * THE MIDDLEMAN KILLER - Logistics Tracking & Telemetry Engine
 */

window.MKLogistics = {
    map: null,
    marker: null,

    initMap() {
        const mapContainer = document.getElementById('logisticsMap');
        if (!mapContainer) return;

        // Check if Leaflet is available
        if (typeof L !== 'undefined') {
            if (this.map) this.map.remove();

            // Anand (22.5645, 72.9289) -> Gandhinagar (23.2156, 72.6369)
            this.map = L.map('logisticsMap').setView([22.8, 72.8], 9);

            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; OpenStreetMap &copy; CARTO',
                maxZoom: 18
            }).addTo(this.map);

            const waypoints = [
                [22.5645, 72.9289], // Anand Farm
                [22.3072, 73.1812], // Vadodara Hub
                [23.2156, 72.6369]  // Gandhinagar Plant
            ];

            const polyline = L.polyline(waypoints, {
                color: '#D96C3B',
                weight: 4,
                opacity: 0.8,
                dashArray: '10, 10'
            }).addTo(this.map);

            // Custom Glowing Marker for Truck
            const truckIcon = L.divIcon({
                className: 'custom-truck-icon',
                html: `<div style="background:#D6A84F; width:20px; height:20px; border-radius:50%; border:3px solid #FFF; box-shadow:0 0 15px #D6A84F;"></div>`,
                iconSize: [20, 20]
            });

            this.marker = L.marker([22.45, 73.05], { icon: truckIcon }).addTo(this.map);
            this.marker.bindPopup("<b>TRK-8849-GJ</b><br>150 Qtl Rice in Transit<br>Temp: 22°C (Nominal)").openPopup();

            this.map.fitBounds(polyline.getBounds());
        }
    }
};
