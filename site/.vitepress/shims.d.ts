// Ambient module declarations for VitePress plugins without bundled types.
declare module 'markdown-it-footnote'

// Vue SFCs imported by VitePress's custom theme need a generic shim
// since VitePress builds via Vite which understands .vue but TypeScript
// project tooling doesn't out of the box. The `any` is intentional —
// we don't need strict typing for component imports here.
declare module '*.vue' {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const component: any
  export default component
}
