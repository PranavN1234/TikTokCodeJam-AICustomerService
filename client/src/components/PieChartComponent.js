import React from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import './PieChartComponent.css';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#AF19FF', '#FF5733'];

const PieChartComponent = ({ data }) => {
  const formattedData = Object.keys(data).map((key, index) => ({
    name: key,
    value: data[key],
    fill: COLORS[index % COLORS.length]
  }));

  return (
    <div className="pie-chart-container">
      <PieChart width={500} height={400} className="pie-chart">
        <Pie
          data={formattedData}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={100}
          fill="#8884d8"
          label
        >
          {formattedData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.fill} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </div>
  );
};

export default PieChartComponent;
