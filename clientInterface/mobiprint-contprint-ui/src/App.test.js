import { render, screen } from '@testing-library/react';
import {expect, jest, test} from '@jest/globals';
import getAngularDir from './api/geomHelper'
import App from './App';
import { AssessmentRounded } from '@mui/icons-material';

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