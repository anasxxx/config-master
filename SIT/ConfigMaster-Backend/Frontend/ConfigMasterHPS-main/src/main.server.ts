if (typeof document !== 'undefined' && !document.createRange) {
  document.createRange = () => {
    const dummyRange: Partial<Range> = {
      setStart: () => {},
      setEnd: () => {},
      commonAncestorContainer: document.body,
      cloneContents: () => document.createDocumentFragment(),
      cloneRange: () => document.createRange(),
      collapse: () => {},
      compareBoundaryPoints: () => 0,
      createContextualFragment: (_: string) =>
        document.createDocumentFragment(),
      deleteContents: () => {},
      detach: () => {},
      extractContents: () => document.createDocumentFragment(),
      getBoundingClientRect: () =>
        ({
          bottom: 0,
          height: 0,
          left: 0,
          right: 0,
          top: 0,
          width: 0,
          x: 0,
          y: 0,
          toJSON: () => ({}),
        } as DOMRect),
      getClientRects: () => {
        const rectList = {
          length: 0,
          item: (index: number): DOMRect | null => null,
          [Symbol.iterator]: function* () {},
        };
        return rectList as unknown as DOMRectList;
      },
      insertNode: () => {},
      selectNode: () => {},
      selectNodeContents: () => {},
      surroundContents: () => {},
    };
    return dummyRange as Range;
  };
}

import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { config } from './app/app.config.server';

const bootstrap = () => bootstrapApplication(AppComponent, config);

export default bootstrap;
