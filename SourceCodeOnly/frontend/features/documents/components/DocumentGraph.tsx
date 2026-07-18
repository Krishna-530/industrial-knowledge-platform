"use client";

import React, { useEffect, useRef } from "react";
import cytoscape from "cytoscape";
import { useDocumentGraph } from "../hooks";
import { Loader2 } from "lucide-react";

interface DocumentGraphProps {
  documentId: string;
}

export function DocumentGraph({ documentId }: DocumentGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  
  const { data, isLoading, isError } = useDocumentGraph(documentId);

  useEffect(() => {
    if (!containerRef.current || !data) return;

    const elements: cytoscape.ElementDefinition[] = [];

    // Add Chunk nodes
    data.chunks?.forEach(chunk => {
      elements.push({
        group: "nodes",
        data: {
          id: chunk.id,
          label: `Chunk ${chunk.index}`,
          type: "chunk",
          content: chunk.text.substring(0, 50) + "..."
        }
      });
    });

    // Add Entity nodes
    data.entities?.forEach(entity => {
      elements.push({
        group: "nodes",
        data: {
          id: entity.id,
          label: entity.name,
          type: "entity",
          category: entity.category
        }
      });
    });

    // Add Relationships (Edges)
    data.relationships?.forEach(rel => {
      elements.push({
        group: "edges",
        data: {
          id: rel.id,
          source: rel.subject_id,
          target: rel.object_id,
          label: rel.predicate,
          score: rel.quality_score
        }
      });
    });

    // Initialize Cytoscape
    cyRef.current = cytoscape({
      container: containerRef.current,
      elements: elements,
      style: [
        {
          selector: 'node[type="chunk"]',
          style: {
            'background-color': '#3b82f6',
            'label': 'data(label)',
            'color': '#fff',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '10px',
            'width': 40,
            'height': 40
          }
        },
        {
          selector: 'node[type="entity"]',
          style: {
            'background-color': '#10b981',
            'label': 'data(label)',
            'color': '#111827',
            'text-valign': 'bottom',
            'text-halign': 'center',
            'font-size': '12px',
            'width': 30,
            'height': 30
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#9ca3af',
            'target-arrow-color': '#9ca3af',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '10px',
            'text-rotation': 'autorotate',
            'text-margin-y': -10
          }
        }
      ],
      layout: {
        name: 'cose',
        idealEdgeLength: 100,
        nodeOverlap: 20,
        refresh: 20,
        fit: true,
        padding: 30,
        randomize: false,
        componentSpacing: 100,
        nodeRepulsion: 400000,
        edgeElasticity: 100,
        nestingFactor: 5,
        gravity: 80,
        numIter: 1000,
        initialTemp: 200,
        coolingFactor: 0.95,
        minTemp: 1.0
      }
    });

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [data]);

  if (isLoading) {
    return (
      <div className="flex h-full min-h-[400px] items-center justify-center bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800">
        <div className="flex flex-col items-center text-gray-500">
          <Loader2 className="h-8 w-8 animate-spin mb-4" />
          <p>Loading Knowledge Graph...</p>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex h-full min-h-[400px] items-center justify-center bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
        <p className="text-red-600 dark:text-red-400">Failed to load graph visualization.</p>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full min-h-[600px] bg-white dark:bg-gray-950 rounded-lg border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
      <div className="absolute top-4 left-4 z-10 bg-white/90 dark:bg-gray-900/90 p-2 rounded shadow text-xs">
        <div className="flex items-center gap-2 mb-1"><div className="w-3 h-3 rounded-full bg-blue-500"></div> Chunks</div>
        <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-emerald-500"></div> Entities</div>
      </div>
      <div ref={containerRef} className="w-full h-full min-h-[600px]" />
    </div>
  );
}
