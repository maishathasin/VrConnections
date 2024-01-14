import { Application } from '../node_modules/@splinetool/runtime'

const canvas = document.getElementById('canvas3d');
const app = new Application(canvas);
app.load('https://prod.spline.design/qt0SmgPY9grBD52j/scene.splinecode');
