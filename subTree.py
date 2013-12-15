#!/usr/bin/env python2

from joern.all import JoernSteps
from PipeTool import PipeTool

from csvAST.CSVToPythonAST import CSVToPythonAST

DESCRIPTION = """Prints all nodes of the AST rooted at the node with
the given id. The default output format is a CSV format similar to
that used of CodeSensor."""

OUTPUT_CSV = 'csv'
OUTPUT_SEXPR = 'sexpr'
OUTPUT_PICKLE= 'pickle'
OUTPUT_FORMATS = [OUTPUT_CSV, OUTPUT_SEXPR, OUTPUT_PICKLE]

class SubTree(PipeTool):
    
    def __init__(self):
        PipeTool.__init__(self, DESCRIPTION)

        self.argParser.add_argument('-O', '--output-format', choices = OUTPUT_FORMATS,
                                    action='store', help="""The output
                                    format to use""",
                                    default = OUTPUT_CSV)
    
        self._initOutputHandlers()

    def _initOutputHandlers(self):
        self.outputHandler = dict()
        self.outputHandler[OUTPUT_CSV] = self._outputCSV
        self.outputHandler[OUTPUT_SEXPR] = self._outputSexpr
        self.outputHandler[OUTPUT_PICKLE] = self._outputPickle
    
    def _outputCSV(self, dbResult):
        for z in dbResult:
            nodeId = z[0]
            x = z[1]
            print '%s\t%s\t%s\t%s' % (nodeId, x[1], x[0]['type'], x[0]['code'])
    
    def _outputSexpr(self, dbResult):
        csvRows = (self._csvRow(z) for z in dbResult)
        converter = CSVToPythonAST()
        converter.processCSVRows(csvRows)
        print converter.getResult()

    def _outputPickle(self, dbResult):
        pass
    
    # @Override
    def streamStart(self):
        self.j = JoernSteps()
        self.j.connectToDatabase()

    # @Override
    def processLine(self, line):
        nodeId = int(line)
        
        query = """g.v(%d).astNodeToSubNodes().transform{ [it[0].id, it] }""" % (nodeId)

        dbResult = self.j.runGremlinQuery(query)
        
        self.outputHandler[self.args.output_format](dbResult)
    
    def _csvRow(self, z):
        nodeId = z[0]
        x = z[1]
        if x[0]['operator'] == None:
            return '%s\t%s\t%s\t%s' % (nodeId, x[1], x[0]['type'], x[0]['code']) 
        else:
            return '%s\t%s\t%s\t%s' % (nodeId, x[1], x[0]['type'], x[0]['operator'])
        

if __name__ == '__main__':
    tool = SubTree()
    tool.run()
