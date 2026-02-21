import { render, screen } from '@testing-library/react';
import {expect, jest, test} from '@jest/globals';
import {getAngularDir, getRobotAngleFromVector } from './api/geomHelper'
import App from './App';
import { AssessmentRounded } from '@mui/icons-material';

// Temp fix to define DOMPoint since it does not work with unit tests
global.DOMPoint = class DOMPoint {
  constructor(x = 0, y = 0) {
    this.x = x;
    this.y = y;
  }
};

// test('renders learn react link', () => {
//   render(<App />);
//   const linkElement = screen.getByText(/learn react/i);
//   expect(linkElement).toBeInTheDocument();
// });

// Patrick does not know what a circle looks like so we are testing the rotation stuff
test('test circle angle and dist work', () => {
  expect(getAngularDir(30, 300)).toEqual(-1)
  expect(getAngularDir(300, 30)).toEqual(1)
  expect(getAngularDir(30, 90)).toEqual(1)
  expect(getAngularDir(90, 30)).toEqual(-1)
});

// Test vector to anlge
test('test circle angle and dist work', () => {
  expect(getRobotAngleFromVector(new DOMPoint(-1, 0))).toEqual(0)
  expect(getRobotAngleFromVector(new DOMPoint(0, -1))).toEqual(90)
  expect(getRobotAngleFromVector(new DOMPoint(1, 0))).toEqual(180)
  expect(getRobotAngleFromVector(new DOMPoint(0, 1))).toEqual(270)

  // Reg cases
  expect(getRobotAngleFromVector(new DOMPoint(-1, -1))).toEqual(45)
  expect(getRobotAngleFromVector(new DOMPoint(1, -1))).toEqual(135)
  expect(getRobotAngleFromVector(new DOMPoint(1, 1))).toEqual(225)
  expect(getRobotAngleFromVector(new DOMPoint(-1, 1))).toEqual(315)
});