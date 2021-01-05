import rhinoscriptsyntax as rs
import math

class LatticeHinge:
    def __init__(self,parameter):
        # LINE_LENGTH = parameter[0]
        # LINE_WIDTH = parameter[1]
        # OVERLAP_RATE = parameter[2]
        # LINE_INTERVAL = parameter[3]
        # INTERVAL_LIMIT = parameter[4]
        self.parameter = parameter
        self.LINE_LENGTH = parameter[0]
        self.LINE_WIDTH = parameter[1]
        self.OVERLAP_RATE = parameter[2]
        self.LINE_INTERVAL = parameter[3]
        self.INTERVAL_LIMIT = parameter[4]
        self.cutAngle = (math.radians(90),math.radians(90),math.radians(90),math.radians(90))

    def setCutAngle(self,cutAngle):
        '''
        Receives:
        cutAngle : tuple (angle,angle,angle,angle)
        '''

        self.cutAngle = cutAngle

    def setParameter(self,parameter):
        self.LINE_LENGTH = parameter[0]
        self.LINE_WIDTH = parameter[1]
        self.OVERLAP_RATE = parameter[2]
        self.LINE_INTERVAL = parameter[3]
        self.INTERVAL_LIMIT = parameter[4]

    def getNextPoint(self,startPoint,length,angle):
        '''
        Receives:
        startPoint : tuple
        length : unsigned
        angle : -90~90

        Returns:
        nextPoint: tuple
        '''
        nextPoint = ( startPoint[0] + length*math.cos(angle),
                      startPoint[1] + length*math.sin(angle),
                      0)

        return nextPoint

    def draw_CutOutline(self,p1,p2):
        '''
        draw  bold line
        p1 : tuple (x,y,z)
        p2 : tuple (x,y,z)
        '''
        lineAngle = math.atan2((p2[1]-p1[1]),(p2[0]-p1[0]))
        length = self.LINE_WIDTH/2

        p1_u = self.getNextPoint(p1,length,lineAngle+math.radians(90))
        p1_d = self.getNextPoint(p1,length,lineAngle+math.radians(-90))
        p2_u = self.getNextPoint(p2,length,lineAngle+math.radians(90))
        p2_d = self.getNextPoint(p2,length,lineAngle+math.radians(-90))

        rs.AddLine(p1_u,p2_u)
        rs.AddLine(p2_u,p2_d)
        rs.AddLine(p2_d,p1_d)
        rs.AddLine(p1_d,p1_u)

    def draw_line(self,p1,p2):
        '''
        When the line is thicker than 0.5mm
        call function draw_CutOutLine
        '''
        if self.LINE_WIDTH < 0.5:
            line = rs.AddLine(p1, p2)
        else:
            draw_CutOutline(p1,p2)

    def draw_lattice_p1(self,start,end):
        '''
        draw lattice line
        difference between p1 and p2 is shifted
        start : tuple (x,y,z)
        end : tuple (x,y,z)
        '''
        gapLength = self.LINE_LENGTH - (self.LINE_LENGTH * self.OVERLAP_RATE)*2

        lineAngle = math.atan2((end[1]-start[1]),(end[0]-start[0]))

        distanceEnd = math.sqrt((start[1]-end[1])**2+(start[0]-end[0])**2)
        point2 = start
        i = 0
        while(1):
        # for j in range(10):
            if i == 0:
                point = self.getNextPoint(point2,gapLength/2,lineAngle)
            else:
                point = self.getNextPoint(point2,gapLength,lineAngle)
            point2 = self.getNextPoint(point,self.LINE_LENGTH,lineAngle)

            distanceP2 = math.sqrt((start[1]-point2[1])**2+(start[0]-point2[0])**2)
            distanceP1 = math.sqrt((start[1]-point[1])**2+(start[0]-point[0])**2)

            if distanceP2 < distanceEnd :
                self.draw_line( point, point2)
                i+=1
            elif distanceP1 < distanceEnd:
                self.draw_line( point, end)
                break
            else:
                break

    def draw_lattice_p2(self,start,end):
        '''
        draw lattice line
        difference between p1 and p2 is shifted
        start : tuple (x,y,z)
        end : tuple (x,y,z)
        '''
        gapLength = self.LINE_LENGTH - (self.LINE_LENGTH * self.OVERLAP_RATE)*2

        lineAngle = math.atan2((end[1]-start[1]),(end[0]-start[0]))

        distanceEnd = math.sqrt((start[1]-end[1])**2+(start[0]-end[0])**2)

        point = start
        i = 0
        while(1):
            if i == 0:
                point2 = self.getNextPoint(point,self.LINE_LENGTH/2,lineAngle)
            else:
                point2 = self.getNextPoint(point,self.LINE_LENGTH,lineAngle)

            distanceP2 = math.sqrt((start[1]-point2[1])**2+(start[0]-point2[0])**2)
            distanceP1 = math.sqrt((start[1]-point[1])**2+(start[0]-point[0])**2)

            if distanceP2 < distanceEnd :
                self.draw_line( point, point2)
                i+=1
            elif distanceP1 < distanceEnd:
                self.draw_line( point, end)
                break
            else:
                break

            point = self.getNextPoint(point2,gapLength,lineAngle) ##Add gap

    def crossPointFilter(self,start,end,cutAngle,d_start,d_end):
        '''
        start : tuple(x,y,z)
        end : tuple(x,y,z)
        for cross point(latticehinges)
        cutAngle : array[3] 0~90
        d_start
        '''
        # print(math.degrees(cutAngle))
        lineAngle = math.atan2((start[1]-end[1]),(start[0]-end[0]))

        d = math.sqrt((start[1]-d_start[1])**2+(start[0]-d_start[0])**2)
        a = abs(d/math.sin(cutAngle))
        crossPoint = (0,0,0)

        crossPoint =( end[0]+a*math.cos(lineAngle+cutAngle),
                      end[1]+a*math.sin(lineAngle+cutAngle),
                      end[2])

        return crossPoint

    def draw_lattice_follow_crosspoint(self,start,end):
        centerPoint = (  start[0] + (end[0]-start[0])/2,
                        start[1] + (end[1]-start[1])/2,
                        0)
        lineAngle = math.atan2((end[1]-start[1]),(end[0]-start[0]))
        count = int(self.INTERVAL_LIMIT/self.LINE_INTERVAL/2)

        self.draw_lattice_p1(centerPoint,start)
        self.draw_lattice_p1(centerPoint,end)

        centerPoint_d = centerPoint_u = centerPoint
        end_d = end_u = end
        start_d = start_u = start

        for i in range(count):
            if i%2:
                centerPoint_u = self.getNextPoint(centerPoint_u,self.LINE_INTERVAL,lineAngle+math.radians(90))
                end_u = self.getNextPoint(end_u,self.LINE_INTERVAL,lineAngle+math.radians(90))
                start_u = self.getNextPoint(start_u,self.LINE_INTERVAL,lineAngle+math.radians(90))
                centerPoint_d = self.getNextPoint(centerPoint_d,self.LINE_INTERVAL,lineAngle+math.radians(-90))
                end_d = self.getNextPoint(end_d,self.LINE_INTERVAL,lineAngle+math.radians(-90))
                start_d = self.getNextPoint(start_d,self.LINE_INTERVAL,lineAngle+math.radians(-90))

                end_u = self.crossPointFilter(centerPoint,end,-self.cutAngle[0],centerPoint_u,end_u)
                self.draw_lattice_p1(centerPoint_u,end_u)

                start_u = self.crossPointFilter(centerPoint,start,self.cutAngle[1],centerPoint_u,start_u)
                self.draw_lattice_p1(centerPoint_u,start_u)

                start_d = self.crossPointFilter(centerPoint,start,-self.cutAngle[2],centerPoint_d,start_d)
                self.draw_lattice_p1(centerPoint_d,start_d)

                end_d = self.crossPointFilter(centerPoint,end,self.cutAngle[3],centerPoint_d,end_d)
                self.draw_lattice_p1(centerPoint_d,end_d)
            else:
                centerPoint_u = self.getNextPoint(centerPoint_u,self.LINE_INTERVAL,lineAngle+math.radians(90))
                end_u = self.getNextPoint(end_u,self.LINE_INTERVAL,lineAngle+math.radians(90))
                start_u = self.getNextPoint(start_u,self.LINE_INTERVAL,lineAngle+math.radians(90))
                centerPoint_d = self.getNextPoint(centerPoint_d,self.LINE_INTERVAL,lineAngle+math.radians(-90))
                end_d = self.getNextPoint(end_d,self.LINE_INTERVAL,lineAngle+math.radians(-90))
                start_d = self.getNextPoint(start_d,self.LINE_INTERVAL,lineAngle+math.radians(-90))

                end_u = self.crossPointFilter(centerPoint,end,-self.cutAngle[0],centerPoint_u,end_u)
                self.draw_lattice_p2(centerPoint_u,end_u)

                start_u = self.crossPointFilter(centerPoint,start,self.cutAngle[1],centerPoint_u,start_u)
                self.draw_lattice_p2(centerPoint_u,start_u)

                start_d = self.crossPointFilter(centerPoint,start,-self.cutAngle[2],centerPoint_d,start_d)
                self.draw_lattice_p2(centerPoint_d,start_d)

                end_d = self.crossPointFilter(centerPoint,end,self.cutAngle[3],centerPoint_d,end_d)
                self.draw_lattice_p2(centerPoint_d,end_d)



if __name__ == '__main__':
	print('no script')
